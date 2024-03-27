import json

import pytest
from fastapi import Response, status
from fastapi.testclient import TestClient
from sqlalchemy import StaticPool, create_engine, text
from sqlalchemy.orm import sessionmaker

from main import app
from ToDoApp.database import Base
from ToDoApp.models import Todos
from ToDoApp.routers.todos import UserInfo, get_current_user, get_db

#################### Setup Dependencies ####################

SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./testdb.db"

test_engine = create_engine(SQLALCHEMY_TEST_DATABASE_URL, connect_args={
    "check_same_thread": False}, poolclass=StaticPool)

TestingSessionLocal = sessionmaker(bind=test_engine, autoflush=False)

Base.metadata.create_all(bind=test_engine)


def override_get_db():
    test_db = TestingSessionLocal()
    try:
        yield test_db
    finally:
        test_db.close()


def override_get_current_user() -> UserInfo:
    fake_user = UserInfo(
        user_id=1,
        username="test_user",
        user_role="admin"
    )
    return fake_user


# dependency
app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user

client = TestClient(app)


@pytest.fixture
def test_todo():
    dummy_todo = Todos(
        title="Learn to code!",
        description="Need to learn everyday!",
        priority=5,
        complete=False,
        owner_id=1
    )
    db = TestingSessionLocal()
    db.add(dummy_todo)
    db.commit()
    yield dummy_todo
    with test_engine.connect() as connection:
        connection.execute(text("DELETE FROM todos;"))
        connection.commit()

#################### Tests ####################


def test_read_all_authenticated(test_todo):
    response: Response = client.get("/todos")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [{'complete': False, 'title': 'Learn to code!',
                                'description': 'Need to learn everyday!', 'id': 1,
                                'priority': 5, 'owner_id': 1}]


def test_read_one_authenticated(test_todo):
    response = client.get("/todo/1")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {'complete': False, 'title': 'Learn to code!',
                               'description': 'Need to learn everyday!', 'id': 1,
                               'priority': 5, 'owner_id': 1}


def test_read_one_authenticated_not_found(test_todo):
    response = client.get("/todo/999")
    print(response.json())
    assert response.status_code == status.HTTP_404_NOT_FOUND

    assert response.json() == {'detail': 'todo not found'}
