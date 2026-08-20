import pytest
import asyncio
from app.services.assessment_engine import assessment_engine

@pytest.mark.asyncio
async def test_single_answer_evaluation_unanswered():
    res = await assessment_engine.evaluate_single_answer(
        question="What is Redis?",
        answer="",
        category="technical"
    )
    assert res["overall_score"] == 0
    assert res["answered"] is False
    assert "skipped" in res["evidence"][0].lower() or "unanswered" in res["evidence"][0].lower()

@pytest.mark.asyncio
async def test_single_answer_evaluation_valid():
    res = await assessment_engine.evaluate_single_answer(
        question="What is overfitting in machine learning?",
        answer="Overfitting occurs when a statistical model memorizes training noise rather than learning generalizable patterns, causing high training performance but poor accuracy on unseen test data.",
        category="technical",
        expected_points=["memorizes training noise", "poor generalization"]
    )
    assert res["overall_score"] > 0
    assert res["answered"] is True
    assert res["technical_accuracy"] >= 0
    assert len(res["ideal_answer_points"]) > 0

def test_speaking_metrics_calculation():
    qna_list = [
        {"question": "Q1", "answer": "I used Python and PyTorch for model training.", "speaking_duration": 5.0, "response_latency": 1.2},
        {"question": "Q2", "answer": "Basically, um, we deployed the API on AWS EC2.", "speaking_duration": 7.0, "response_latency": 1.5}
    ]
    metrics = assessment_engine.calculate_speaking_metrics(qna_list)
    assert metrics is not None
    assert metrics["is_voice_interview"] is True
    assert metrics["total_words"] > 0
    assert metrics["words_per_minute"] > 0
    assert metrics["filler_word_count"] >= 2  # 'basically', 'um'

def test_skill_evidence_matrix_minimum_evidence_rule():
    evaluations = [
        {"overall_score": 85, "answered": True},
        {"overall_score": 90, "answered": True}
    ]
    qna_list = [
        {"question": "Python Q1", "question_type": "Python"},
        {"question": "SQL Q1", "question_type": "SQL"}
    ]
    matrix = assessment_engine.build_skill_matrix(evaluations, qna_list)
    assert len(matrix) == 2
    for item in matrix:
        assert item["questions_tested"] == 1
        assert "Limited evidence" in item["evidence_confidence"]

def test_deterministic_score_aggregation_unassessed_exclusion():
    evaluations = [
        {
            "technical_accuracy": 90,
            "problem_solving": 80,
            "project_understanding": 85,
            "communication": 80,
            "relevance": 85,
            "overall_score": 85,
            "answered": True,
            "user_answer": "ans1"
        },
        {
            "technical_accuracy": 85,
            "problem_solving": 85,
            "project_understanding": 80,
            "communication": 85,
            "relevance": 85,
            "overall_score": 85,
            "answered": True,
            "user_answer": "ans2"
        },
        {
            "technical_accuracy": 80,
            "problem_solving": 80,
            "project_understanding": 80,
            "communication": 80,
            "relevance": 80,
            "overall_score": 80,
            "answered": True,
            "user_answer": "ans3"
        }
    ]
    qna_list = [
        {"question": "System Design Q1", "question_type": "System Design", "answer": "ans1"},
        {"question": "System Design Q2", "question_type": "System Design", "answer": "ans2"},
        {"question": "System Design Q3", "question_type": "System Design", "answer": "ans3"}
    ]
    scores = assessment_engine.compute_deterministic_overall_scores(evaluations, qna_list)
    assert scores["coding_score"] is None
    assert scores["category_scores"]["coding"] is None
    assert scores["overall_score"] is not None
    assert 50 <= scores["overall_score"] <= 100
