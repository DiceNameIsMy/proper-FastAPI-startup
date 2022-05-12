import pytest
from requests.models import Response

from fastapi.testclient import TestClient

from domain.user import UserDomain, DomainError
from repository.models import User
from settings import settings


URI = f"/v{settings.api_version}/profile"


def test_valid(
    client: TestClient,
    user_domain: UserDomain,
    verified_user: User,
    user_auth_token: str,
):
    user_id = verified_user.id
    response: Response = client.delete(
        URI,
        headers={
            "Content-Type": "Application/json",
            "Authorization": f"Bearer {user_auth_token}",
        },
    )
    assert response.status_code == 204, response.json()
    with pytest.raises(DomainError):
        user_domain.get_by_id(user_id)


def test_not_enough_rights(
    client: TestClient,
    user_domain: UserDomain,
    verified_user: User,
    user_auth_token_only_profile: str,
):
    user_id = verified_user.id
    response: Response = client.delete(
        URI,
        headers={
            "Content-Type": "Application/json",
            "Authorization": f"Bearer {user_auth_token_only_profile}",
        },
    )
    assert response.status_code == 401, response.json()
    assert user_domain.get_by_id(user_id), response.json()
