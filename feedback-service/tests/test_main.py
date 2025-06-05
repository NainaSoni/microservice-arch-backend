from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import Base, get_db
from app.models import Feedback
import pytest

# Test database URL
SQLALCHEMY_DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/test_feedback_db"

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
        connection.execute("TRUNCATE TABLE feedbacks RESTART IDENTITY CASCADE")
        connection.commit()
    # Drop all tables after all tests are done
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(test_db):
    with TestClient(app) as test_client:
        yield test_client

def test_create_feedback(client):
    response = client.post(
        "/feedback/",
        json={"feedback": "Great team culture!"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["feedback"] == "Great team culture!"
    assert "id" in data
    assert data["is_deleted"] == False

def test_get_feedbacks(client):
    # Create a feedback first
    client.post(
        "/feedback/",
        json={"feedback": "Great team culture!"}
    )
    
    response = client.get("/feedback/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["feedback"] == "Great team culture!"

def test_delete_feedbacks(client):
    # Create a feedback first
    client.post(
        "/feedback/",
        json={"feedback": "Great team culture!"}
    )
    
    response = client.delete("/feedback/")
    assert response.status_code == 200
    assert response.json()["message"] == "All feedbacks have been soft deleted"
    
    # Verify feedback is soft deleted
    get_response = client.get("/feedback/")
    assert len(get_response.json()) == 0 