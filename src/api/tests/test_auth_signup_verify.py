import pytest

from requests.models import Response

from sqlalchemy.orm.session import Session
from sqlalchemy.orm.exc import NoResultFound

from fastapi.testclient import TestClient

from repository.models import User, VerificationCode
from repository.user import get_user_by_email, get_verification_code
from settings import settings


URI = f"/v{settings.api_version}/signup/verify"


def test_valid_code(
    client: TestClient,
    db: Session,
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
    assert response.status_code == 200
    assert get_user_by_email(db, unverified_user.email).is_email_verified

    with pytest.raises(NoResultFound):
        get_verification_code(db, unverified_user.id, code)


def test_already_verified(
    client: TestClient,
    db: Session,
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
    assert response.status_code == 400
    assert get_user_by_email(db, verified_user.email).is_email_verified
    with pytest.raises(NoResultFound):
        get_verification_code(db, verified_user.id, code)
