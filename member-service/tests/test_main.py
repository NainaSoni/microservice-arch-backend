from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import Base, get_db
from app.models import Member
import pytest

# Test database URL
SQLALCHEMY_DATABASE_URL = "postgresql://postgres:postgres@localhost:5433/test_member_db"

# Create test database engine
engine = create_engine(SQLALCHEMY_DATABASE_URL)
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
    with engine.connect() as connection:
        connection.execute("TRUNCATE TABLE members RESTART IDENTITY CASCADE")
        connection.commit()
    # Drop all tables after all tests are done
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(test_db):
    with TestClient(app) as test_client:
        yield test_client

def test_create_member(client):
    member_data = {
        "first_name": "John",
        "last_name": "Doe",
        "login": "john123",
        "avatar_url": "https://example.com/avatar.jpg",
        "followers": 120,
        "following": 35,
        "title": "Senior Developer",
        "email": "john@example.com"
    }
    
    response = client.post("/members/", json=member_data)
    assert response.status_code == 200
    data = response.json()
    assert data["first_name"] == member_data["first_name"]
    assert data["last_name"] == member_data["last_name"]
    assert data["login"] == member_data["login"]
    assert "id" in data
    assert data["is_deleted"] == False

def test_get_members(client):
    # Create two members with different follower counts
    member1 = {
        "first_name": "John",
        "last_name": "Doe",
        "login": "john123",
        "avatar_url": "https://example.com/avatar1.jpg",
        "followers": 120,
        "following": 35,
        "title": "Senior Developer",
        "email": "john@example.com"
    }
    
    member2 = {
        "first_name": "Jane",
        "last_name": "Smith",
        "login": "jane456",
        "avatar_url": "https://example.com/avatar2.jpg",
        "followers": 200,
        "following": 50,
        "title": "Lead Developer",
        "email": "jane@example.com"
    }
    
    client.post("/members/", json=member1)
    client.post("/members/", json=member2)
    
    response = client.get("/members/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    # Verify sorting by followers (descending)
    assert data[0]["followers"] == 200
    assert data[1]["followers"] == 120

def test_delete_members(client):
    # Create a member first
    member_data = {
        "first_name": "John",
        "last_name": "Doe",
        "login": "john123",
        "avatar_url": "https://example.com/avatar.jpg",
        "followers": 120,
        "following": 35,
        "title": "Senior Developer",
        "email": "john@example.com"
    }
    
    client.post("/members/", json=member_data)
    
    response = client.delete("/members/")
    assert response.status_code == 200
    assert response.json()["message"] == "All members have been soft deleted"
    
    # Verify member is soft deleted
    get_response = client.get("/members/")
    assert len(get_response.json()) == 0 