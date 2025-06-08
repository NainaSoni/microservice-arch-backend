import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import Base, get_db
from app import models
from shared.error_handling import ErrorCode

# Set environment variables for Docker
os.environ["RUNNING_IN_DOCKER"] = "1"
os.environ["DATABASE_URL"] = "postgresql://postgres:postgres@feedback-db:5432/feedback_db"

# Create the engine using the environment variable
engine = create_engine(os.environ["DATABASE_URL"])
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="function")
def test_db():
    # Create all tables
    Base.metadata.create_all(bind=engine)
    yield
    # Clean up all data after each test
    with engine.begin() as connection:
        connection.execute("TRUNCATE TABLE feedbacks RESTART IDENTITY CASCADE")
    # Drop all tables after all tests are done
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(test_db):
    return TestClient(app)

def test_create_feedback_success(client):
    response = client.post(
        "/feedback/",
        json={
            "feedback": "Great service!"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["feedback"] == "Great service!"
    assert "id" in data
    assert "created_at" in data
    assert "is_deleted" in data
    assert data["is_deleted"] == False

def test_get_feedbacks_success(client):
    # First create a feedback
    client.post(
        "/feedback/",
        json={
            "feedback": "Great service!"
        }
    )
    
    response = client.get("/feedback/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["feedback"] == "Great service!"

def test_get_feedbacks_empty(client):
    response = client.get("/feedback/")
    assert response.status_code == 400
    data = response.json()
    assert data["error_code"] == ErrorCode.NO_DATA_FOUND_ERROR.value
    assert data["message"] == "No active feedbacks found"

def test_delete_feedbacks_success(client):
    # First create a feedback
    client.post(
        "/feedback/",
        json={
            "feedback": "Great service!"
        }
    )
    
    response = client.delete("/feedback/")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "All feedbacks have been soft deleted"
    
    # Verify feedbacks are soft deleted
    response = client.get("/feedback/")
    assert response.status_code == 400
    data = response.json()
    assert data["error_code"] == ErrorCode.NO_DATA_FOUND_ERROR.value
    assert data["message"] == "No active feedbacks found"

def test_delete_single_feedback_success(client):
    # First create a feedback
    response = client.post(
        "/feedback/",
        json={
            "feedback": "Great service!"
        }
    )
    feedback_id = response.json()["id"]
    
    # Delete the feedback
    response = client.delete(f"/feedback/{feedback_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == f"Feedback with id {feedback_id} has been soft deleted"
    
    # Verify feedback is soft deleted
    response = client.get("/feedback/")
    assert response.status_code == 400
    data = response.json()
    assert data["error_code"] == ErrorCode.NO_DATA_FOUND_ERROR.value
    assert data["message"] == "No active feedbacks found"

def test_delete_single_feedback_not_found(client):
    response = client.delete("/feedback/999")
    assert response.status_code == 400
    data = response.json()
    assert data["error_code"] == ErrorCode.NOT_FOUND_ERROR.value
    assert data["message"] == "Feedback with id 999 not found"

def test_delete_single_member_success(client):
    # First create a member
    response = client.post(
        "/member/",
        json={
            "login": "testuser",
            "password": "testpassword123"
        }
    )
    member_id = response.json()["id"]
    
    # Delete the member
    response = client.delete(f"/member/{member_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == f"Member with id {member_id} has been soft deleted"

def test_delete_single_member_not_found(client):
    response = client.delete("/member/999")
    assert response.status_code == 400
    data = response.json()
    assert data["error_code"] == ErrorCode.NOT_FOUND_ERROR.value
    assert data["message"] == "Member with id 999 not found"

