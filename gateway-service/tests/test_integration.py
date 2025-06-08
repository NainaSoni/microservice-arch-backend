import os
import pytest
from fastapi.testclient import TestClient
from app.main import app
import random

# Set environment variables for testing
os.environ["MEMBER_SERVICE_URL"] = "http://localhost:8002"
os.environ["FEEDBACK_SERVICE_URL"] = "http://localhost:8001"

@pytest.fixture(scope="function", autouse=True)
def setup_and_cleanup():
    """
    Ensure the test user exists before each test and hard delete test user after each test.
    """
    client = TestClient(app)
    user_data = {
        "first_name": "Test",
        "last_name": "User",
        "login": "testuser",
        "email": "test.user@example.com",
        "password": "testpassword123"
    }
    # Create the user if it doesn't exist
    token_response = client.post(
        "/token",
        data={"username": "testuser", "password": "testpassword123"}
    )
    if token_response.status_code != 200:
        client.post("/members/", json=user_data)
    yield
    # Hard delete testuser after test
    token_response = client.post(
        "/token",
        data={"username": "testuser", "password": "testpassword123"}
    )
    if token_response.status_code == 200:
        token = token_response.json()["access_token"]
        members = client.get("/members/", headers={"Authorization": f"Bearer {token}"})
        for member in members.json():
            if member["login"] == "testuser":
                client.delete(f"/internal/members/{member['id']}/hard", headers={"Authorization": f"Bearer {token}"})
                break
        # Hard delete all feedback
        feedbacks = client.get("/feedback/", headers={"Authorization": f"Bearer {token}"})
        for feedback in feedbacks.json():
            client.delete(f"/internal/feedback/{feedback['id']}/hard", headers={"Authorization": f"Bearer {token}"})

@pytest.fixture(scope="function")
def client():
    return TestClient(app)

def test_login_success(client):
    response = client.post(
        "/token",
        data={"username": "testuser", "password": "testpassword123"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "token_type" in data
    assert data["token_type"] == "bearer"

def test_login_invalid_credentials(client):
    response = client.post(
        "/token",
        data={"username": "invalid", "password": "invalid"}
    )
    assert response.status_code == 401

def test_create_member_success(client):
    # First get token
    token_response = client.post(
        "/token",
        data={"username": "testuser", "password": "testpassword123"}
    )
    token = token_response.json()["access_token"]
    # Create member
    response = client.post(
        "/members/",
        json={
            "first_name": "1Test",
            "last_name": "1User",
            "login": "1testuser2",
            "email": "test.user@example.com",
            "password": "testpassword123"
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    print(f"Create Member Response: {response.json()}")
    assert response.status_code == 200
    

def test_get_members_success(client):
    # First get token
    token_response = client.post(
        "/token",
        data={"username": "testuser", "password": "testpassword123"}
    )
    token = token_response.json()["access_token"]
    response = client.get(
        "/members/",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_delete_single_member_success(client):
    # First get token
    token_response = client.post(
        "/token",
        data={"username": "testuser", "password": "testpassword123"}
    )
    token = token_response.json()["access_token"]
    # Create a member with random login and email
    random_suffix = random.randint(1, 1000)
    member_data = {
        "first_name": "Test",
        "last_name": "User",
        "login": f"testuser{random_suffix}",
        "email": f"test.user{random_suffix}@example.com",
        "password": "testpassword123"
    }
    create_response = client.post(
        "/members/",
        json=member_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    print(f"Create Member Response: {create_response.json()}")
    member_id = create_response.json()["id"]
    # Delete the member
    response = client.delete(
        f"/members/{member_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    print(f"Delete Member Response: {response.json()}")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == f"Member with id {member_id} has been soft deleted"
    # Clean up by hard deleting the member
    client.delete(f"/internal/members/{member_id}/hard", headers={"Authorization": f"Bearer {token}"})

def test_create_feedback_success(client):
    # First get token
    token_response = client.post(
        "/token",
        data={"username": "testuser", "password": "testpassword123"}
    )
    token = token_response.json()["access_token"]
    # Create feedback
    response = client.post(
        "/feedback/",
        json={
            "feedback": "Great service!"
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    print(f"Create Feedback Response: {response.json()}")
    assert response.status_code == 200
    data = response.json()
    assert data["feedback"] == "Great service!"

def test_get_feedback_success(client):
    # First get token
    token_response = client.post(
        "/token",
        data={"username": "testuser", "password": "testpassword123"}
    )
    token = token_response.json()["access_token"]
    response = client.get(
        "/feedback/",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_delete_single_feedback_success(client):
    # First get token
    token_response = client.post(
        "/token",
        data={"username": "testuser", "password": "testpassword123"}
    )
    token = token_response.json()["access_token"]
    # Create feedback with random data
    feedback_data = {
        "feedback": f"Random feedback {random.randint(1, 1000)}"
    }
    create_response = client.post(
        "/feedback/",
        json=feedback_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    feedback_id = create_response.json()["id"]
    # Delete the feedback
    response = client.delete(
        f"/feedback/{feedback_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == f"Feedback with id {feedback_id} has been soft deleted"
    # Clean up by hard deleting the feedback
    client.delete(f"/internal/feedback/{feedback_id}/hard", headers={"Authorization": f"Bearer {token}"})

def test_unauthorized_access(client):
    # Try to access protected endpoint without token
    response = client.get("/members/")
    assert response.status_code == 401

def test_invalid_token(client):
    # Try to access protected endpoint with invalid token
    response = client.get(
        "/members/",
        headers={"Authorization": "Bearer invalid_token"}
    )
    print(f"Invalid Token Response: {response.json()}")
    assert response.status_code == 401