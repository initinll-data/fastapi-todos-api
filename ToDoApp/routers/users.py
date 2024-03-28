from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, status
from passlib.context import CryptContext
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from ToDoApp.database import SessionLocal
from ToDoApp.models import Users

from .auth import UserInfo, get_current_user

router = APIRouter(
    prefix="/users",
    tags=["users"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# dependency
db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[UserInfo, Depends(get_current_user)]
bcrypt_context = CryptContext(schemes=['bcrypt'])


class UserVerification(BaseModel):
    password: str
    new_password: str = Field(min_length=6)


@router.get("/user", status_code=status.HTTP_200_OK)
async def get_user(user: user_dependency, db: db_dependency):
    try:
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed !")

        user_info = db.query(Users).filter(Users.id == user.user_id).first()

        if user_info is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="user not found")

        return user_info
    except HTTPException:
        raise
    except Exception as e:
        error = f"An exception of type {
            type(e).__name__} occurred. Details: {str(e)}"
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=error)


@router.put("/password", status_code=status.HTTP_204_NO_CONTENT)
async def change_password(user: user_dependency, db: db_dependency, user_verification: UserVerification):
    try:
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed !")

        user_model = db.query(Users).filter(Users.id == user.user_id).first()

        if user_model is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="user not found")\

        if not bcrypt_context.verify(user_verification.password, user_model.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect password")

        user_model.hashed_password = bcrypt_context.hash(
            user_verification.new_password)
        db.add(user_model)
        db.commit()
    except HTTPException:
        raise
    except Exception as e:
        error = f"An exception of type {
            type(e).__name__} occurred. Details: {str(e)}"
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=error)
