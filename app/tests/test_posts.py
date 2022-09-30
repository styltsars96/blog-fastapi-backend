"""
Tests for posts functionality
"""
import asyncio

from fastapi.testclient import TestClient

from app.main import app
from app.schemas.users import UserCreate
from app.utils.users import create_new_user, create_user_token
from app.tests.test_users import SIGNUP_DATA


TEST_NAME = "Stelios"
TEST_PASSWD = "shepard"

POST_REQUEST_DATA = {
    "title": "Hello",
    "post_content": "I am the vanguard of your destruction",
}
POST_UPDATE_DATA = {
    "title": "Hi",
    "post_content": "I'm commander Shepard, and this is my favorite project on the Citadel.",
}


def test_create_post(temp_db):
    """
    Dummy post creation for a dummy authenticated user.
    """
    user = UserCreate(**SIGNUP_DATA)
    request_data = POST_REQUEST_DATA
    with TestClient(app) as client:
        # Create user and use their token to add new post
        loop = asyncio.get_event_loop()
        user_db = loop.run_until_complete(create_new_user(user))
        response = client.put(
            "/posts",
            json=request_data,
            headers={"Authorization": f"Bearer {user_db.token.token}"},
        )
    assert response.status_code == 201
    assert response.json()["id"] == 1
    assert response.json()["title"] == POST_REQUEST_DATA["title"]
    assert response.json()["post_content"] == POST_REQUEST_DATA["post_content"]


def test_create_post_forbidden_without_token(temp_db):
    """
    Post creation without token should return 401.
    """
    request_data = POST_REQUEST_DATA
    with TestClient(app) as client:
        response = client.put("/posts", json=request_data)
    assert response.status_code == 401


def test_posts_list(temp_db):
    """
    Get a list of posts. (Assuming that test_create_post succeeded)
    """
    with TestClient(app) as client:
        response = client.get("/posts")
    assert response.status_code == 200
    assert response.json()["total_count"] == 1
    assert response.json()["results"][0]["id"] == 1
    assert response.json()["results"][0]["title"] == POST_REQUEST_DATA["title"]
    assert (
        response.json()["results"][0]["post_content"]
        == POST_REQUEST_DATA["post_content"]
    )


def test_post_detail(temp_db):
    """
    Get a post detail for the first dummy post. (Assuming that test_create_post succeeded)
    """
    post_id = 1
    with TestClient(app) as client:
        response = client.get(f"/posts/{post_id}")
    assert response.status_code == 200
    assert response.json()["id"] == 1
    assert response.json()["title"] == POST_REQUEST_DATA["title"]
    assert response.json()["post_content"] == POST_REQUEST_DATA["post_content"]


def test_update_post(temp_db):
    """
    Update the dummy post. (Assuming that test_create_post succeeded)
    """
    post_id = 1
    request_data = POST_UPDATE_DATA
    with TestClient(app) as client:
        # Create user token to add new post
        loop = asyncio.get_event_loop()
        token = loop.run_until_complete(create_user_token(user_id=1))
        response = client.post(
            f"/posts/{post_id}",
            json=request_data,
            headers={"Authorization": f"Bearer {token.token}"},
        )
    assert response.status_code == 200
    assert response.json()["id"] == 1
    assert response.json()["title"] == POST_UPDATE_DATA["title"]
    assert response.json()["post_content"] == POST_UPDATE_DATA["post_content"]


def test_update_post_forbidden_without_token(temp_db):
    """
    Update of dummy post without token should return 401.
    """
    post_id = 1
    request_data = POST_UPDATE_DATA
    with TestClient(app) as client:
        response = client.post(f"/posts/{post_id}", json=request_data)
    assert response.status_code == 401
