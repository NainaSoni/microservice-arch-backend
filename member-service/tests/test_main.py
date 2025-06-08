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
os.environ["DATABASE_URL"] = "postgresql://postgres:postgres@member-db:5432/member_db"

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
        connection.execute("TRUNCATE TABLE members RESTART IDENTITY CASCADE")
    # Drop all tables after all tests are done
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(test_db):
    return TestClient(app)

def test_create_member_success(client):
    response = client.post(
        "/members/",
        json={
            "first_name": "N",
            "last_name": "S",
            "login": "s123",
            "email": "n.s@example1.com",
            "avatar_url": "https://example.com/avatars/n.jpg",
            "followers": 100,
            "following": 50,
            "title": "Software Engineer"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["first_name"] == "N"
    assert data["last_name"] == "S"
    assert data["login"] == "s123"
    assert data["email"] == "n.s@example1.com"
    assert data["avatar_url"] == "https://example.com/avatars/n.jpg"
    assert data["followers"] == 100
    assert data["following"] == 50
    assert data["title"] == "Software Engineer"
    assert "id" in data
    assert "created_at" in data
    assert "is_deleted" in data
    assert data["is_deleted"] == False

def test_create_member_duplicate_login(client):
    # First create a member
    client.post(
        "/members/",
        json={
            "first_name": "G",
            "last_name": "S",
            "login": "g123",
            "email": "g.s@example.com",
            "avatar_url": "https://example.com/avatars/g.jpg",
            "followers": 100,
            "following": 50,
            "title": "Software Engineer"
        }
    )
    
    # Try to create another member with same login
    response = client.post(
        "/members/",
        json={
            "first_name": "G",
            "last_name": "S",
            "login": "g123",
            "email": "g.s@example.com",
            "avatar_url": "https://example.com/avatars/g.jpg",
            "followers": 50,
            "following": 25,
            "title": "Product Manager"
        }
    )
    assert response.status_code == 400
    data = response.json()
    assert data["error_code"] == ErrorCode.DUPLICATE_DATA_ERROR.value
    assert data["message"] == "Member with this login already exists"
    assert "login" in data["details"]

def test_get_members_success(client):
    # First create a member
    client.post(
        "/members/",
        json={
            "first_name": "N",
            "last_name": "S",
            "login": "s123",
            "email": "n.s@example1.com",
            "avatar_url": "https://example.com/avatars/n.jpg",
            "followers": 100,
            "following": 50,
            "title": "Software Engineer"
        }
    )
    
    response = client.get("/members/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["first_name"] == "N"
    assert data[0]["last_name"] == "S"
    assert data[0]["login"] == "s123"
    assert data[0]["email"] == "n.s@example1.com"
    assert data[0]["avatar_url"] == "https://example.com/avatars/n.jpg"
    assert data[0]["followers"] == 100
    assert data[0]["following"] == 50
    assert data[0]["title"] == "Software Engineer"

def test_get_members_empty(client):
    response = client.get("/members/")
    assert response.status_code == 400
    data = response.json()
    assert data["error_code"] == ErrorCode.NO_DATA_FOUND_ERROR.value
    assert data["message"] == "No active members found"

def test_delete_members_success(client):
    # First create a member
    client.post(
        "/members/",
        json={
            "first_name": "N",
            "last_name": "S",
            "login": "s123",
            "email": "n.s@example1.com",
            "avatar_url": "https://example.com/avatars/n.jpg",
            "followers": 100,
            "following": 50,
            "title": "Software Engineer"
        }
    )
    
    response = client.delete("/members/")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "All members have been soft deleted"
    
    # Verify members are soft deleted
    response = client.get("/members/")
    assert response.status_code == 400
    data = response.json()
    assert data["error_code"] == ErrorCode.NO_DATA_FOUND_ERROR.value
    assert data["message"] == "No active members found"

def test_delete_members_empty(client):
    response = client.delete("/members/")
    assert response.status_code == 400
    data = response.json()
    assert data["error_code"] == ErrorCode.NO_DATA_FOUND_ERROR.value
    assert data["message"] == "No active members found to delete"

def test_delete_single_member_success(client):
    # First create a member
    response = client.post(
        "/members/",
        json={
            "first_name": "N",
            "last_name": "S",
            "login": "s123",
            "email": "n.s@example1.com",
            "avatar_url": "https://example.com/avatars/n.jpg",
            "followers": 100,
            "following": 50,
            "title": "Software Engineer"
        }
    )
    member_id = response.json()["id"]
    
    # Delete the member
    response = client.delete(f"/members/{member_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == f"Member with id {member_id} has been soft deleted"
    
    # Verify member is soft deleted
    response = client.get("/members/")
    assert response.status_code == 400
    data = response.json()
    assert data["error_code"] == ErrorCode.NO_DATA_FOUND_ERROR.value
    assert data["message"] == "No active members found"

def test_delete_single_member_not_found(client):
    response = client.delete("/members/999")
    assert response.status_code == 400
    data = response.json()
    assert data["error_code"] == ErrorCode.NOT_FOUND_ERROR.value
    assert data["message"] == "Member with id 999 not found"
