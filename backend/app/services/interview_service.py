import uuid
import logging
import json
import asyncio
from typing import List, Dict, Any, Optional
from app.services.ai_service import ai_service
from app.services.prompts import get_interviewer_system_prompt
from app.schemas.interview import QuestionResponse

logger = logging.getLogger(__name__)

class InterviewService:
    @staticmethod
    def get_fallback_questions(
        role: str,
        experience_level: str,
        interview_type: str,
        count: int,
        interview_style: str = "Professional",
        candidate_profile: Optional[Dict[str, Any]] = None
    ) -> List[QuestionResponse]:
        c_name = candidate_profile.get("name", "Candidate") if candidate_profile and isinstance(candidate_profile, dict) else "Candidate"
        skills = candidate_profile.get("skills", []) if candidate_profile and isinstance(candidate_profile, dict) else []
        skills_str = ", ".join([str(s) for s in skills[:4]]) if isinstance(skills, list) and skills else "core technical skills"
        projects = candidate_profile.get("projects", []) if candidate_profile and isinstance(candidate_profile, dict) else []
        
        proj_name = "your primary project"
        if isinstance(projects, list) and len(projects) > 0:
            if isinstance(projects[0], dict):
                proj_name = projects[0].get("name", "your primary project")
            elif isinstance(projects[0], str):
                proj_name = projects[0]

        default_questions = [
            QuestionResponse(
                question_order=1,
                category=f"{interview_type.capitalize()} Warm-up",
                question_text=f"Hi {c_name}, welcome to your {interview_style} {interview_type} interview for {role}. Can you introduce yourself and walk me through your key contributions in {proj_name}?",
                key_aspects=["Background", "Project Ownership", "Communication"]
            ),
            QuestionResponse(
                question_order=2,
                category=f"{interview_type.capitalize()} Technical",
                question_text=f"Regarding {proj_name}, how specifically did you utilize {skills_str}? What architectural tradeoffs or challenges did you evaluate?",
                key_aspects=["Technical Accuracy", "Skill Mastery", "Architecture Tradeoffs"]
            ),
            QuestionResponse(
                question_order=3,
                category=f"{interview_type.capitalize()} Deep-Dive",
                question_text=f"Walk me through the system design, data flow, and error-handling mechanisms in {proj_name}. How did you ensure high reliability and scalability?",
                key_aspects=["Scalability", "System Design", "Error Handling"]
            ),
            QuestionResponse(
                question_order=4,
                category="Behavioral & STAR",
                question_text=f"Describe a high-stakes technical disagreement, bug, or tight deadline you experienced while building {proj_name}. How did you resolve it under pressure?",
                key_aspects=["STAR Method", "Conflict Resolution", "Pressure Management"]
            ),
            QuestionResponse(
                question_order=5,
                category="Optimization & Edge Cases",
                question_text=f"If traffic, throughput, or workload for {proj_name} increased by 10x overnight, where would performance bottlenecks occur and how would you re-architect it?",
                key_aspects=["Performance Optimization", "Scalability Bottlenecks", "System Monitoring"]
            )
        ]
        
        res = []
        for i in range(count):
            base_q = default_questions[i % len(default_questions)]
            res.append(QuestionResponse(
                question_order=i + 1,
                category=base_q.category,
                question_text=base_q.question_text,
                key_aspects=base_q.key_aspects
            ))
        return res

    async def generate_questions(
        self,
        role: str,
        experience: str,
        industry: str,
        interview_type: str,
        difficulty: str,
        interview_style: str = "Professional",
        candidate_profile: Optional[Dict[str, Any]] = None,
        count: int = 5
    ) -> List[QuestionResponse]:
        system_prompt = get_interviewer_system_prompt(role, experience, interview_type)
        
        profile_summary = ""
        if candidate_profile and isinstance(candidate_profile, dict):
            profile_summary = f"""
            MANDATORY CANDIDATE RESUME EVIDENCE:
            Name: {candidate_profile.get('name', 'Candidate')}
            Target Role: {candidate_profile.get('target_role', role)}
            Skills: {json.dumps(candidate_profile.get('skills', []))}
            Projects: {json.dumps(candidate_profile.get('projects', []))}
            Work History / Experience: {json.dumps(candidate_profile.get('experience', candidate_profile.get('work_history', [])))}
            Education: {json.dumps(candidate_profile.get('education', []))}
            """

        user_prompt = f"""
        You are an expert interviewer. Generate EXACTLY {count} distinct, highly specific interview questions strictly tailored to:

        1. TARGET ROLE & INDUSTRY: {role} ({experience} level) in {industry}
        2. INTERVIEW TYPE: {interview_type} (e.g. Technical, Coding, System Design, Medical Coding, HR/Behavioral, Aptitude)
        3. INTERVIEW STYLE: {interview_style} (e.g. Strict Technical Depth, Friendly & Encouraging, Professional, HR + Technical)
        4. DIFFICULTY LEVEL: {difficulty}

        {profile_summary}

        CRITICAL INSTRUCTIONS:
        - EVERY question MUST directly cite the candidate's ACTUAL resume projects, specific skills, or work experience when provided!
        - Match the interviewer tone defined in INTERVIEW STYLE ({interview_style}).
        - Match the interview domain defined in INTERVIEW TYPE ({interview_type}).

        Return JSON array matching this exact schema:
        [
            {{
                "question_order": 1,
                "category": "{interview_type.capitalize()}",
                "question": "Question text directly referencing candidate background...",
                "key_aspects": ["Technical depth", "Problem solving"]
            }}
        ]
        """

        try:
            res = await asyncio.wait_for(
                ai_service.generate_json(
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ]
                ),
                timeout=10.0
            )
            if isinstance(res, list) and len(res) > 0:
                questions = []
                for idx, item in enumerate(res):
                    q_text = item.get("question") or item.get("question_text") or ""
                    if q_text.strip():
                        questions.append(QuestionResponse(
                            question_order=item.get("question_order", idx + 1),
                            category=item.get("category", interview_type.capitalize()),
                            question_text=q_text.strip(),
                            key_aspects=item.get("key_aspects", ["Technical Depth", "Domain Knowledge"])
                        ))
                if len(questions) >= count:
                    return questions[:count]
                elif len(questions) > 0:
                    # Pad with fallback questions if LLM returned fewer than count
                    fallbacks = self.get_fallback_questions(role, experience, interview_type, count, interview_style, candidate_profile)
                    for f in fallbacks[len(questions):]:
                        questions.append(f)
                    return questions
        except Exception as e:
            logger.warning(f"Notice: LLM question generation fallback invoked ({e}). Returning candidate resume tailored questions.")

        return self.get_fallback_questions(role, experience, interview_type, count, interview_style, candidate_profile)

interview_service = InterviewService()
