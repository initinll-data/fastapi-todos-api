import pytest
from fastapi.testclient import TestClient
from sqlalchemy import StaticPool, create_engine, text
from sqlalchemy.orm import sessionmaker

from main import app
from ToDoApp.database import Base
from ToDoApp.models import Todos, Users
from ToDoApp.routers.auth import bcrypt_context
from ToDoApp.routers.todos import UserInfo

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
        username="codingwithrobytest",
        user_role="admin"
    )
    return fake_user


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


@pytest.fixture
def test_user():
    dummy_user = Users(
        username="codingwithrobytest",
        email="codingwithrobytest@email.com",
        first_name="Eric",
        last_name="Roby",
        hashed_password=bcrypt_context.hash("testpassword"),
        role="admin",
        is_active=True
    )
    db = TestingSessionLocal()
    db.add(dummy_user)
    db.commit()
    yield dummy_user
    with test_engine.connect() as connection:
        connection.execute(text("DELETE FROM users;"))
        connection.commit()
