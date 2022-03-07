from requests.models import Response

from fastapi.testclient import TestClient

from repository.models import User


URI = "/v1/login"


def test_login_valid_user(client: TestClient, regular_user: User):
    response: Response = client.post(
        URI,
        data={"username": regular_user.email, "password": "password"},
    )
    assert response.json().get("token")
    assert response.status_code == 200


def test_invalid_password(client: TestClient, regular_user: User):
    response: Response = client.post(
        URI,
        data={"username": regular_user.email, "password": "bad_password"},
    )
    assert response.status_code == 401


def test_user_does_not_exist(client: TestClient):
    response: Response = client.post(
        URI,
        data={"username": "not_existing@test.test", "password": "password"},
    )
    assert response.status_code == 401
