from requests.models import Response

from sqlalchemy.orm.session import Session

from fastapi.testclient import TestClient

from crud.user import get_user_by_email, create_user
from schemas.user import UserToCreateSchema


URI = "/v1/signup"


def test_signup_valid_user(client: TestClient, db: Session):
    response: Response = client.post(
        URI,
        json={"email": "valid@test.test", "password": "password"},
        headers={"Content-Type": "Application/json"},
    )
    assert response.json().get("email") == "valid@test.test"
    assert response.status_code == 201

    assert get_user_by_email(db, "valid@test.test") is not None


def test_signup_bad_email(client: TestClient, db: Session):
    response: Response = client.post(
        URI,
        json={"email": "invalid_email", "password": "password"},
        headers={"Content-Type": "Application/json"},
    )
    assert response.status_code == 422
    assert get_user_by_email(db, "invalid_email") is None


def test_signup_existing_email(client: TestClient, db: Session):
    create_user(
        db, UserToCreateSchema(email="existing_email@test.test", password="password")
    )
    response: Response = client.post(
        URI,
        json={"email": "existing_email@test.test", "password": "password"},
        headers={"Content-Type": "Application/json"},
    )
    assert response.status_code == 400
    assert get_user_by_email(db, "existing_email@test.test") is not None
