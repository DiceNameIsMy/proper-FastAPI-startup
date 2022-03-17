import pytest

from requests.models import Response

from sqlalchemy.orm.session import Session
from sqlalchemy.exc import NoResultFound

from fastapi.testclient import TestClient

from repository.models import User, VerificationCode
from repository.crud.user import get_user_by_email, get_verification_code


URI = "/v1/signup/verify"


def test_valid_code(
    client: TestClient,
    db: Session,
    email_not_verified_user: User,
    email_not_verified_user_signup_token: str,
    email_not_verified_user_verification_code: VerificationCode,
):
    code = email_not_verified_user_verification_code.code
    response: Response = client.post(
        URI,
        json={"code": code},
        headers={
            "Content-Type": "Application/json",
            "Authorization": f"Bearer {email_not_verified_user_signup_token}",
        },
    )
    assert response.status_code == 200
    assert get_user_by_email(db, email_not_verified_user.email).is_email_verified

    with pytest.raises(NoResultFound):
        get_verification_code(db, email_not_verified_user.id, code)


def test_already_verified(
    client: TestClient,
    db: Session,
    email_already_verified_user: User,
    email_not_verified_user_signup_token: str,
    email_not_verified_user_verification_code: VerificationCode,
):
    code = email_not_verified_user_verification_code.code
    response: Response = client.post(
        URI,
        json={"code": code},
        headers={
            "Content-Type": "Application/json",
            "Authorization": f"Bearer {email_not_verified_user_signup_token}",
        },
    )
    assert response.status_code == 400
    assert get_user_by_email(db, email_already_verified_user.email).is_email_verified
    assert get_verification_code(db, email_already_verified_user.id, code)
