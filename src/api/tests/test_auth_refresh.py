from requests.models import Response

from fastapi.testclient import TestClient
from domain.user import UserDomain

from settings import settings


URI = f"/v{settings.api_version}/token/refresh"


def test_valid(
    client: TestClient,
    user_domain: UserDomain,
    user_refresh_token: str,
):
    response: Response = client.post(
        URI,
        json={"refresh_token": user_refresh_token},
        headers={"Content-Type": "Application/json"},
    )
    assert response.status_code == 200, response.json()
    assert user_domain.read_token(response.json().get("access_token"))


def test_bad_token(
    client: TestClient,
    user_refresh_token: str,
):
    response: Response = client.post(
        URI,
        json={"refresh_token": user_refresh_token + "bad"},
        headers={"Content-Type": "Application/json"},
    )
    assert response.status_code == 400, response.json()


def test_empty_token(
    client: TestClient,
):
    response: Response = client.post(
        URI,
        json={"refresh_token": ""},
        headers={"Content-Type": "Application/json"},
    )
    assert response.status_code == 400, response.json()
