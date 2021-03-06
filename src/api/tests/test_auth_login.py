from requests.models import Response

from fastapi.testclient import TestClient

from repository.models import User
from settings import settings


URI = f"/v{settings.api_version}/login"


def test_valid_user(client: TestClient, verified_user: User):
    response: Response = client.post(
        URI,
        data={"username": verified_user.email, "password": "password"},
    )
    assert response.json().get("access_token")
    assert response.status_code == 200


def test_invalid_password(client: TestClient, verified_user: User):
    response: Response = client.post(
        URI,
        data={"username": verified_user.email, "password": "bad_password"},
    )
    assert response.status_code == 401


def test_user_does_not_exist(client: TestClient):
    response: Response = client.post(
        URI,
        data={"username": "not_existing_test@gmail.com", "password": "password"},
    )
    assert response.status_code == 401


def test_not_verified_user(client: TestClient, unverified_user: User):
    response: Response = client.post(
        URI,
        data={"username": unverified_user.email, "password": "bad_password"},
    )
    assert response.status_code == 401


def test_user_from_sso_without_password(client: TestClient, user_from_sso: User):
    response: Response = client.post(
        URI,
        data={"username": user_from_sso.email, "password": "bad_password"},
    )
    assert response.status_code == 401
