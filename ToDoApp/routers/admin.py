from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from ToDoApp.database import SessionLocal
from ToDoApp.models import Todos

from .auth import UserInfo, get_current_user

router = APIRouter(
    prefix="/admin",
    tags=["admin"]
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


@router.get("/todo", status_code=status.HTTP_200_OK)
async def read_all(user: user_dependency, db: db_dependency):
    try:
        if user is None or user.user_role != "admin":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed !")

        todos = db.query(Todos).all()

        if todos is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="not found")

        return todos
    except HTTPException:
        raise
    except Exception as e:
        error = f"An exception of type {
            type(e).__name__} occurred. Details: {str(e)}"
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=error)


@router.delete("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(user: user_dependency, db: db_dependency, todo_id: int = Path(gt=0)):
    try:
        if user is None or user.user_role != 'admin':
            raise HTTPException(
                status_code=401, detail='Authentication Failed')
        todo_model = db.query(Todos).filter(Todos.id == todo_id).first()

        if todo_model is None:
            raise HTTPException(status_code=404, detail='not found')
        db.query(Todos).filter(Todos.id == todo_id).delete()
        db.commit()
    except HTTPException:
        raise
    except Exception as e:
        error = f"An exception of type {
            type(e).__name__} occurred. Details: {str(e)}"
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=error)
