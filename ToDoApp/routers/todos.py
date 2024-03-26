from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from ToDoApp.database import SessionLocal
from ToDoApp.models import Todos

from .auth import UserInfo, get_current_user

router = APIRouter(
    tags=["todos"]
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


class TodoRequest(BaseModel):
    title: str = Field(min_length=3)
    description: str = Field(min_length=3, max_length=100)
    priority: int = Field(gt=0, lt=6)
    complete: bool = Field(default=False)


@router.get("/todos", status_code=status.HTTP_200_OK)
async def read_all(user: user_dependency, db: db_dependency):
    try:
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication failed")

        todos = db.query(Todos) \
            .filter(Todos.owner_id == user.user_id) \
            .all()

        if todos is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="not found")

        return todos
    except Exception as e:
        error = f"An exception of type {
            type(e).__name__} occurred. Details: {str(e)}"
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=error)


@router.get("/todo/{todo_id}", status_code=status.HTTP_200_OK)
async def read_todo(user: user_dependency, db: db_dependency, todo_id: int = Path(gt=0)):
    try:
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication failed")

        todo_model = db.query(Todos) \
            .filter(Todos.id == todo_id) \
            .filter(Todos.owner_id == user.user_id) \
            .first()

        if todo_model is not None:
            return todo_model

        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="todo not found")
    except Exception as e:
        error = f"An exception of type {
            type(e).__name__} occurred. Details: {str(e)}"
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=error)


@router.post("/todo", status_code=status.HTTP_201_CREATED)
async def create_todo(user: user_dependency, db: db_dependency, todo_request: TodoRequest):
    try:
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication failed")
        todo_model = Todos(** todo_request.model_dump(),
                           owner_id=user.user_id)
        db.add(todo_model)
        db.commit()
    except Exception as e:
        error = f"An exception of type {
            type(e).__name__} occurred. Details: {str(e)}"
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=error)


@router.put("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_todo(user: user_dependency, db: db_dependency, todo_request: TodoRequest, todo_id: int = Path(gt=0)):
    try:
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication failed")

        todo_model = db.query(Todos) \
            .filter(Todos.id == todo_id) \
            .filter(Todos.owner_id == user.user_id) \
            .first()

        if todo_model is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="todo not found")

        todo_model.title = todo_request.title
        todo_model.description = todo_request.description
        todo_model.priority = todo_request.priority
        todo_model.complete = todo_request.complete

        db.add(todo_model)
        db.commit()
    except Exception as e:
        error = f"An exception of type {
            type(e).__name__} occurred. Details: {str(e)}"
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=error)


@router.delete("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(user: user_dependency, db: db_dependency, todo_id: int = Path(gt=0)):
    try:
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication failed")

        todo_model = db.query(Todos) \
            .filter(Todos.id == todo_id) \
            .filter(Todos.owner_id == user.user_id) \
            .first()

        if todo_model is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="todo not found")

        db.delete(todo_model)
        db.commit()
    except Exception as e:
        error = f"An exception of type {
            type(e).__name__} occurred. Details: {str(e)}"
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=error)
