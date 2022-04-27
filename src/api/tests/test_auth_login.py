from requests.models import Response

from fastapi.testclient import TestClient

from repository.models import User
from settings import settings


URI = f"/v{settings.api_version}/login"


def test_valid_user(client: TestClient, regular_user: User):
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
        data={"username": "not_existing_test@gmail.com", "password": "password"},
    )
    assert response.status_code == 401


def test_not_verified_user(client: TestClient, email_not_verified_user: User):
    response: Response = client.post(
        URI,
        data={"username": email_not_verified_user.email, "password": "bad_password"},
    )
    assert response.status_code == 401
