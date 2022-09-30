"""
Tests for users functionality
"""
import asyncio
import pytest

from fastapi.testclient import TestClient

from app.main import app
from app.schemas.users import UserCreate
from app.utils.users import create_new_user, create_user_token

USERNAME = "Stelios_Shepard"
OTHER_USERNAME = "Jane_Shepard"
PASSWORD = "#This_is_my_favorite_store_on_the_citadel1"
OTHER_PASSWORD = "$Assuming_control1"

USER_BASE_DATA = {
    "username": USERNAME,
    "password": PASSWORD,
}

FALSE_BASE_DATA = {
    "username": USERNAME,
    "password": OTHER_PASSWORD,
}

OTHER_BASE_DATA = {
    "username": OTHER_USERNAME,
    "password": OTHER_PASSWORD,
}

SIGNUP_DATA = {
    **USER_BASE_DATA,
    "short_biography": "I am commander Shepard",
    "birth_date": "1989-09-30",
    "country": "Canada",
    "city": "Vancouver",
}

FALSE_SIGNUP_DATA = {
    **OTHER_BASE_DATA,
    "short_biography": "We are Harbinger",
    "birth_date": "1989-09-30",
    "country": "Dark",
    "city": "Space",
}


def test_sign_up(temp_db):
    """test_sign_up
    Test new user sign-up: Passed
    """
    with TestClient(app) as client:
        response = client.post("/sign-up", json=SIGNUP_DATA)
    assert response.status_code == 200
    assert response.json()["username"] == USERNAME
    assert response.json()["token"]["expires"] is not None
    assert response.json()["token"]["access_token"] is not None


def test_login(temp_db):
    """test_login
    Test dummy user login (assuming test_sign_up succeeded)
    """
    with TestClient(app) as client:
        response = client.post("/auth", data=USER_BASE_DATA)
    assert response.status_code == 200
    assert response.json()["token_type"] == "bearer"
    assert response.json()["expires"] is not None
    assert response.json()["access_token"] is not None


def test_login_with_invalid_password(temp_db):
    """test_login_with_invalid_password
    Login with invalid password should return 400
    """
    with TestClient(app) as client:
        response = client.post("/auth", data=FALSE_BASE_DATA)
    assert response.status_code == 400


def test_user_detail(temp_db):
    """test_user_detail
    Get user details (assuming test_sign_up succeeded)
    """
    with TestClient(app) as client:
        # Create user token to see user info
        loop = asyncio.get_event_loop()
        token = loop.run_until_complete(create_user_token(user_id=1))
        response = client.get(
            "/me/profile", headers={"Authorization": f"Bearer {token.token}"}
        )
    assert response.status_code == 200
    assert response.json()["id"] == 1
    assert response.json()["username"] == USERNAME


def test_user_detail_forbidden_without_token(temp_db):
    """test_user_detail_forbidden_without_token
    Getting user details without token should return 401
    """
    with TestClient(app) as client:
        response = client.get("/me/profile")
    assert response.status_code == 401


@pytest.mark.freeze_time("2020-05-05")
def test_user_detail_forbidden_with_expired_token(temp_db, freezer):
    """test_user_detail_forbidden_with_expired_token
    After a token is expired, user details endpoint should return 401
    """
    user = UserCreate(**FALSE_SIGNUP_DATA)
    with TestClient(app) as client:
        # Create user and use expired token
        loop = asyncio.get_event_loop()
        user_auth_response = loop.run_until_complete(create_new_user(user))
        freezer.move_to("'2020-12-01'")
        response = client.get(
            "/me/profile",
            headers={"Authorization": f"Bearer {user_auth_response.token.token}"},
        )
    assert response.status_code == 401
