import pytest
from fastapi.testclient import TestClient
from app.database import Base, engine
import app.models  # noqa: F401
from app.main import app

Base.metadata.create_all(bind=engine)
client = TestClient(app)

def test_mock_interview_full_flow():
    # 1. Start mock interview
    start_resp = client.post("/api/mock-interviews/start", json={
        "role": "AI/ML Engineer",
        "experience_level": "Mid-Level",
        "interview_type": "technical",
        "difficulty": "medium",
        "duration_minutes": 30
    })
    assert start_resp.status_code == 200
    data = start_resp.json()
    assert "session_id" in data
    assert data["role"] == "AI/ML Engineer"
    assert "first_question" in data
    assert "question" in data["first_question"]

    session_id = data["session_id"]
    first_q = data["first_question"]["question"]

    # 2. Submit candidate answer
    answer_resp = client.post(f"/api/mock-interviews/{session_id}/answer", json={
        "question": first_q,
        "answer": "I built a real-time object detection pipeline using YOLOv8, optimizing inference with PyTorch and FastAPI."
    })
    assert answer_resp.status_code == 200

    # 3. Evaluate candidate answer
    eval_resp = client.post(f"/api/mock-interviews/{session_id}/evaluate", json={
        "question": first_q,
        "answer": "I built a real-time object detection pipeline using YOLOv8, optimizing inference with PyTorch and FastAPI."
    })
    assert eval_resp.status_code == 200
    eval_data = eval_resp.json()
    assert "score" in eval_data
    assert "technical_accuracy" in eval_data
    assert "relevance" in eval_data

    # 4. Request next question
    next_resp = client.post(f"/api/mock-interviews/{session_id}/next-question", json={
        "current_question": first_q,
        "last_answer": "I built a real-time object detection pipeline using YOLOv8.",
        "previous_questions": [first_q]
    })
    assert next_resp.status_code == 200
    next_data = next_resp.json()
    assert "question" in next_data

    # 5. Finish mock interview & generate report
    finish_resp = client.post(f"/api/mock-interviews/{session_id}/finish")
    assert finish_resp.status_code == 200
    finish_data = finish_resp.json()
    assert finish_data["status"] == "completed"
    assert "report" in finish_data
