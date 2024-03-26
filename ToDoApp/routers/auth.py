import datetime
from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ToDoApp.database import SessionLocal

from ..models import Users

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

SECRET_KEY = 'zDIin1ap584IFwOnmJvDOqWXjz8yJDc3azeHoYLtrsuqIrR483QR8vyIG2B8c07cr9Aq4kfr9DzCT0Jm'
ALGORITHM = 'HS256'

bcrypt_context = CryptContext(schemes=['bcrypt'])
oauth2_bearer = OAuth2PasswordBearer(tokenUrl='auth/token')


class CreateUserRequest(BaseModel):
    username: str
    email: str
    first_name: str
    last_name: str
    password: str
    role: str


class Token(BaseModel):
    access_token: str
    token_type: str


class UserInfo(BaseModel):
    username: str
    user_id: int
    user_role: str


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# dependencies
db_dependency = Annotated[Session, Depends(get_db)]


def authenticate_user(username: str, password: str, db: Session) -> Users | bool:
    try:
        user = db.query(Users).filter(Users.username == username).first()

        if not user:
            return False
        if not bcrypt_context.verify(password, user.hashed_password):
            return False

        return user
    except:
        raise


def create_access_token(username: str, user_id: int, role: str, expires_delta: timedelta) -> str:
    try:
        payload = {'sub': username, 'id': user_id, 'role': role}
        # Create a timezone-aware datetime object representing the current time in UTC
        now_in_utc = datetime.datetime.now(datetime.UTC)
        # Add delta to the current time
        expires = now_in_utc + expires_delta
        payload.update({'exp': expires})

        return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    except:
        raise


async def get_current_user(token: Annotated[UserInfo, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
        username: str = payload.get('sub')
        user_id: str = payload.get('id')
        user_role: str = payload.get('role')

        if username is None or user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail='could not validate user')

        user_info = UserInfo(user_id=int(user_id),
                             username=username, user_role=user_role)

        return user_info
    except:
        raise


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(db: db_dependency, create_user_request: CreateUserRequest):
    try:
        create_user_model = Users(
            email=create_user_request.email,
            username=create_user_request.username,
            first_name=create_user_request.first_name,
            last_name=create_user_request.last_name,
            hashed_password=bcrypt_context.hash(create_user_request.password),
            role=create_user_request.role,
            is_active=True
        )
        db.add(create_user_model)
        db.commit()
    except Exception as e:
        error = f"An exception of type {
            type(e).__name__} occurred. Details: {str(e)}"
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=error)


@router.post("/token", status_code=status.HTTP_200_OK, response_model=Token)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_dependency):
    try:
        user = authenticate_user(form_data.username, form_data.password, db)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail='could not validate user')

        token = create_access_token(
            user.username, user.id, user.role, timedelta(minutes=20))

        return {'access_token': token, 'token_type': 'bearer'}
    except Exception as e:
        error = f"An exception of type {
            type(e).__name__} occurred. Details: {str(e)}"
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=error)
