from fastapi import Response, status

from main import app
from ToDoApp.routers.users import get_current_user, get_db

from .utils import (
    TestingSessionLocal,
    client,
    override_get_current_user,
    override_get_db,
    test_user,
)

#################### Dependencies Override ####################

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user

#################### Tests ####################


def test_return_user(test_user):
    response: Response = client.get("/users/user")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()['username'] == 'codingwithrobytest'
    assert response.json()['email'] == 'codingwithrobytest@email.com'
    assert response.json()['first_name'] == 'Eric'
    assert response.json()['last_name'] == 'Roby'
    assert response.json()['role'] == 'admin'


def test_change_password_success(test_user):
    response: Response = client.put("/users/password", json={"password": "testpassword",
                                                             "new_password": "newpassword"})
    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_change_password_invalid_current_password(test_user):
    response: Response = client.put("/users/password", json={"password": "wrong_password",
                                                             "new_password": "newpassword"})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {'detail': 'Incorrect password'}
