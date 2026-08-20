import json
import logging
from typing import Dict, Any, List, Optional
from app.services.ai_service import ai_service
from app.services.question_classifier import classify_interview_question
from app.prompts.interview_bit import get_interview_bit_prompt

logger = logging.getLogger(__name__)

class InterviewBitService:
    def classify(self, question: str) -> Dict[str, Any]:
        return classify_interview_question(question)

    def generate_follow_ups(self, category: str, question: str) -> List[str]:
        return []

    async def generate_answer(
        self,
        question: str,
        profile: Dict[str, Any],
        history: List[Dict[str, str]] = [],
        style: str = "normal"
    ) -> Dict[str, Any]:
        classification = self.classify(question)
        category = classification.get("category", "general")
        system_prompt = get_interview_bit_prompt(profile, style)

        messages = [{"role": "system", "content": system_prompt}] + history[-6:] + [{"role": "user", "content": question}]

        try:
            answer = await ai_service.generate(messages=messages, temperature=0.7)
        except Exception as e:
            logger.error(f"Interview Bit LLM error: {e}")
            answer = f"I'm here to help answer your question regarding **{question}**. (Note: AI service encountered an error: {str(e)})"

        follow_ups = self.generate_follow_ups(category, question)

        return {
            "question": question,
            "category": category,
            "answer": answer,
            "profile_used": bool(profile),
            "follow_ups": follow_ups
        }

interview_bit_service = InterviewBitService()
