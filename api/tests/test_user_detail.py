from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)


def test_admin_can_view_any_user():
    response = client.get(
        "/api/users/2",
        headers={"Authorization": "Bearer 1:admin"},
    )
    assert response.status_code == 200
    assert response.json()["username"] == "test_user"


def test_user_can_view_self():
    response = client.get(
        "/api/users/2",
        headers={"Authorization": "Bearer 2:user"},
    )
    assert response.status_code == 200
    assert response.json()["id"] == 2


def test_user_cannot_view_others():
    response = client.get(
        "/api/users/1",
        headers={"Authorization": "Bearer 2:user"},
    )
    assert response.status_code == 403


def test_user_not_found():
    response = client.get(
        "/api/users/999",
        headers={"Authorization": "Bearer 1:admin"},
    )
    assert response.status_code == 404
