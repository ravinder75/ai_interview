import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import Base, get_db
from app.services.password_service import hash_password

# Setup test DB
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_interview.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

client = TestClient(app)

def test_health():
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "healthy"

def test_auth_register_and_login():
    reg_data = {
        "name": "Jane Tester",
        "email": "jane@example.com",
        "password": "SecurePassword123!",
        "target_role": "Backend Developer",
        "experience_level": "Fresher",
        "programming_languages": ["Python", "SQL"],
        "terms_accepted": True
    }
    res = client.post("/api/auth/register", json=reg_data)
    assert res.status_code == 201
    data = res.json()
    assert "access_token" in data
    assert data["user"]["email"] == "jane@example.com"

    # Login
    login_res = client.post("/api/auth/login", json={
        "email": "jane@example.com",
        "password": "SecurePassword123!"
    })
    assert login_res.status_code == 200
    assert "access_token" in login_res.json()

def test_schedule_interview():
    req = {
        "role": "Frontend Developer",
        "type": "technical_behavioral",
        "difficulty": "medium",
        "duration_minutes": 30,
        "programming_language": "TypeScript"
    }
    res = client.post("/api/interviews/schedule", json=req)
    assert res.status_code == 200
    data = res.json()
    assert data["role"] == "Frontend Developer"
    assert data["status"] == "scheduled"
