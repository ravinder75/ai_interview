import pytest
from app.services.assessment_engine import assessment_engine

@pytest.mark.asyncio
async def test_zero_answer_session_report():
    session_info = {
        "session_id": "test-zero-answers",
        "role": "Full-Stack Developer"
    }
    candidate_profile = {
        "name": "Alex Candidate",
        "target_role": "Full-Stack Developer"
    }
    qna_list = [] # Zero answers submitted

    report = await assessment_engine.generate_assessment_report(
        session_info=session_info,
        candidate_profile=candidate_profile,
        qna_list=qna_list
    )

    assert report["report_type"] == "NO_RESPONSE"
    assert report["status"] == "EXITED"
    assert report["trust_label"] == "No Evidence"
    assert report["evidence_level"] == "NONE"
    assert report["overall_score"] is None
    assert report["technical_score"] is None
    assert report["problem_solving_score"] is None
    assert report["project_understanding_score"] is None
    assert report["role_knowledge_score"] is None
    assert report["communication_score"] is None
    assert report["coding_score"] is None
    assert report["consistency_score"] is None
    assert report["questions_answered"] == 0
    assert report["completion_percentage"] == 0.0

@pytest.mark.asyncio
async def test_hard_validation_rule_throws_error():
    invalid_report = {
        "overall_score": 66,
        "category_scores": {"technical": 60}
    }
    with pytest.raises(ValueError) as excinfo:
        assessment_engine.validate_report_consistency(invalid_report, answered_cnt=0)
    
    assert "HARD VALIDATION ERROR" in str(excinfo.value)

@pytest.mark.asyncio
async def test_single_answer_partial_report():
    session_info = {
        "session_id": "test-single-answer",
        "role": "AI Engineer"
    }
    candidate_profile = {
        "name": "Sam Candidate",
        "target_role": "AI Engineer"
    }
    qna_list = [
        {
            "question": "What is overfitting?",
            "answer": "Overfitting happens when a model fits training noise and generalizes poorly to unseen data.",
            "category": "technical",
            "difficulty": "medium"
        }
    ]

    report = await assessment_engine.generate_assessment_report(
        session_info=session_info,
        candidate_profile=candidate_profile,
        qna_list=qna_list
    )

    assert report["report_type"] == "PARTIAL"
    assert report["questions_answered"] == 1
    assert report["consistency_score"] is None # Consistency requires >= 3 answers
    assert report["overall_score"] is None # Overall score requires >= 3 answers
    assert report["technical_score"] is not None # Technical was evaluated

@pytest.mark.asyncio
async def test_full_session_five_answers_report():
    evaluations = [
        {"answered": True, "user_answer": "ans1", "overall_score": 85, "technical_accuracy": 85, "problem_solving": 80, "project_understanding": 90, "communication": 85, "relevance": 85},
        {"answered": True, "user_answer": "ans2", "overall_score": 90, "technical_accuracy": 90, "problem_solving": 85, "project_understanding": 85, "communication": 90, "relevance": 90},
        {"answered": True, "user_answer": "ans3", "overall_score": 80, "technical_accuracy": 80, "problem_solving": 80, "project_understanding": 80, "communication": 80, "relevance": 80},
    ]
    qna_list = [
        {"question": "Q1", "answer": "ans1", "category": "technical"},
        {"question": "Q2", "answer": "ans2", "category": "technical"},
        {"question": "Q3", "answer": "ans3", "category": "technical"},
    ]

    scores = assessment_engine.compute_deterministic_overall_scores(evaluations, qna_list)

    assert scores["overall_score"] is not None
    assert scores["overall_score"] >= 75
    assert scores["consistency_score"] is not None # >= 3 answers evaluated
