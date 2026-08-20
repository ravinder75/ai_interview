import logging
from typing import Dict, Any, List
from app.services.ai_service import ai_service
from app.services.assessment_engine import assessment_engine
from app.schemas.ai import AnswerEvaluationResponse, StarScore

logger = logging.getLogger(__name__)

class FeedbackService:
    async def evaluate_answer(
        self,
        question: str,
        answer: str,
        job_title: str = "Software Engineer",
        job_description: str = ""
    ) -> AnswerEvaluationResponse:
        eval_res = await assessment_engine.evaluate_single_answer(
            question=question,
            answer=answer,
            job_title=job_title,
            job_description=job_description
        )

        star_score = StarScore(
            situation=8,
            task=8,
            action=8,
            result=8
        )

        return AnswerEvaluationResponse(
            overall_score=eval_res["overall_score"],
            clarity=eval_res["communication"],
            relevance=eval_res["relevance"],
            confidence=int(eval_res["evaluation_confidence"] * 100),
            structure=eval_res["answer_structure"],
            technical_depth=eval_res["technical_accuracy"],
            star_analysis=star_score,
            strengths=eval_res["strengths"],
            improvements=eval_res["weaknesses"],
            suggested_answer=f"To answer '{question}', cover: " + ", ".join(eval_res.get("ideal_answer_points", ["Direct definition", "Architecture details", "Concrete metrics"])),
            follow_up_questions=["What trade-offs would you consider if scaling this 10x?"]
        )

    async def generate_full_interview_report(
        self,
        profile: Dict[str, Any],
        session_info: Dict[str, Any],
        qna_list: list
    ) -> Dict[str, Any]:
        return await assessment_engine.generate_assessment_report(
            session_info=session_info,
            candidate_profile=profile,
            qna_list=qna_list
        )

feedback_service = FeedbackService()
