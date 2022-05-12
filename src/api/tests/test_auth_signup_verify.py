import pytest

from requests.models import Response

from sqlalchemy.orm.exc import NoResultFound

from fastapi.testclient import TestClient

from repository.models import User, VerificationCode
from repository.user import UserRepository
from settings import settings


URI = f"/v{settings.api_version}/signup/verify"


def test_valid_code(
    client: TestClient,
    user_repository: UserRepository,
    unverified_user: User,
    unverified_user_signup_token: str,
    unverified_user_verification_code: VerificationCode,
):
    code = unverified_user_verification_code.code
    response: Response = client.post(
        URI,
        json={"code": code},
        headers={
            "Content-Type": "Application/json",
            "Authorization": f"Bearer {unverified_user_signup_token}",
        },
    )
    assert response.status_code == 200, response.json()
    assert user_repository.get_by_email(unverified_user.email).is_email_verified

    with pytest.raises(NoResultFound):
        user_repository.get_verification_code(unverified_user.id, code)


def test_already_verified(
    client: TestClient,
    user_repository: UserRepository,
    verified_user: User,
    unverified_user_signup_token: str,
    unverified_user_verification_code: VerificationCode,
):
    code = unverified_user_verification_code.code
    response: Response = client.post(
        URI,
        json={"code": code},
        headers={
            "Content-Type": "Application/json",
            "Authorization": f"Bearer {unverified_user_signup_token}",
        },
    )
    assert response.status_code == 400, response.json()
    assert user_repository.get_by_email(verified_user.email).is_email_verified
    with pytest.raises(NoResultFound):
        user_repository.get_verification_code(verified_user.id, code)
