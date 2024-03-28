from fastapi import Response, status

from main import app
from ToDoApp.models import Todos
from ToDoApp.routers.admin import UserInfo, get_current_user, get_db

from .utils import (
    TestingSessionLocal,
    client,
    override_get_current_user,
    override_get_db,
    test_todo,
)

#################### Dependencies Override ####################

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user

#################### Tests ####################


def test_admin_read_all_authenticated(test_todo):
    response: Response = client.get("/admin/todo")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [{'complete': False, 'title': 'Learn to code!',
                                'description': 'Need to learn everyday!', 'id': 1,
                                'priority': 5, 'owner_id': 1}]


def test_admin_delete_todo(test_todo):
    response: Response = client.delete("/admin/todo/1")
    assert response.status_code == status.HTTP_204_NO_CONTENT
    db = TestingSessionLocal()
    model = db.query(Todos).filter(Todos.id == 1).first()
    assert model is None


def test_admin_delete_todo_not_found():
    response: Response = client.delete("/admin/todo/9999")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {'detail': 'not found'}
