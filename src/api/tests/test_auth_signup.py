import pytest
from requests.models import Response

from sqlalchemy.orm.session import Session
from sqlalchemy.orm.exc import NoResultFound

from fastapi.testclient import TestClient

from repository.user import get_user_by_email
from domain.user import UserDomain
from schemas.user import UserToCreateSchema
from settings import settings


URI = f"/v{settings.api_version}/signup"


def test_valid_user(client: TestClient, db: Session):
    response: Response = client.post(
        URI,
        json={"email": "test@gmail.com", "password": "password"},
        headers={"Content-Type": "Application/json"},
    )
    assert response.status_code == 201, response.json()
    assert response.json().get("user").get("email") == "test@gmail.com", response.json()

    assert get_user_by_email(db, "test@gmail.com")


def test_bad_email(client: TestClient, db: Session):
    response: Response = client.post(
        URI,
        json={"email": "invalid_email", "password": "password"},
        headers={"Content-Type": "Application/json"},
    )
    assert response.status_code == 422
    with pytest.raises(NoResultFound):
        get_user_by_email(db, "invalid_email")


def test_existing_email(client: TestClient, user_domain: UserDomain):
    user_domain.create(
        UserToCreateSchema(email="existing_email_test@gmail.com", password="password")
    )
    response: Response = client.post(
        URI,
        json={"email": "existing_email_test@gmail.com", "password": "password"},
        headers={"Content-Type": "Application/json"},
    )
    assert response.status_code == 400
    assert user_domain.get_by_email("existing_email_test@gmail.com")
