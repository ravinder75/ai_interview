import re
import json
import hashlib
import logging
import statistics
from typing import Dict, Any, List, Optional
from datetime import datetime

from app.services.ai_service import ai_service
from app.services.prompts.assessment_prompts import (
    get_answer_evaluator_prompt,
    get_report_synthesizer_prompt,
    ANSWER_EVALUATOR_PROMPT_VERSION,
    REPORT_SYNTHESIZER_PROMPT_VERSION
)

logger = logging.getLogger(__name__)

# Difficulty weights
DIFFICULTY_WEIGHTS = {
    "easy": 0.8,
    "medium": 1.0,
    "hard": 1.2
}

# Category Weights for Overall Performance Score calculation
# Technical: 30%, Problem Solving: 15%, Project: 15%, Role Knowledge: 15%, Communication: 10%, Coding: 10%, Consistency: 5%
CATEGORY_WEIGHTS = {
    "technical": 0.30,
    "problem_solving": 0.15,
    "project": 0.15,
    "role_knowledge": 0.15,
    "communication": 0.10,
    "coding": 0.10,
    "consistency": 0.05
}

COMMON_FILLER_WORDS = {"um", "uh", "like", "you know", "actually", "basically", "sort of", "kind of"}

class AssessmentEngine:
    def __init__(self):
        self.engine_version = "v3.0.0"

    def compute_evidence_hash(self, qna_list: List[Dict[str, Any]]) -> str:
        raw_str = json.dumps(qna_list, sort_keys=True)
        return hashlib.sha256(raw_str.encode("utf-8")).hexdigest()[:16]

    async def evaluate_single_answer(
        self,
        question: str,
        answer: str,
        category: str = "technical",
        difficulty: str = "medium",
        job_title: str = "Software Engineer",
        job_description: str = "",
        expected_points: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Runs an independent evaluation for a single Q&A pair."""
        cleaned_answer = (answer or "").strip()

        # Handle empty/skipped answer deterministically
        if not cleaned_answer or len(cleaned_answer) < 5 or "not answered" in cleaned_answer.lower():
            return {
                "technical_accuracy": 0,
                "relevance": 0,
                "completeness": 0,
                "depth": 0,
                "reasoning": 0,
                "problem_solving": 0,
                "project_understanding": 0,
                "communication": 0,
                "answer_structure": 0,
                "evaluation_confidence": 1.0,
                "overall_score": 0,
                "strengths": [],
                "weaknesses": ["No response or insufficient response provided for this question."],
                "missing_concepts": expected_points or ["Required key technical concepts"],
                "factual_corrections": [],
                "evidence": ["Question was skipped or unanswered."],
                "ideal_answer_points": expected_points or ["Provide direct structured explanation"],
                "follow_up_needed": True,
                "answered": False
            }

        prompt_data = get_answer_evaluator_prompt(
            question=question,
            answer=cleaned_answer,
            category=category,
            difficulty=difficulty,
            job_title=job_title,
            job_description=job_description,
            expected_points=expected_points
        )

        try:
            res = await ai_service.generate_json(
                messages=[
                    {"role": "system", "content": prompt_data["system"]},
                    {"role": "user", "content": prompt_data["user"]}
                ]
            )

            # Clamp scores strictly between 0 and 100
            tech_acc = min(100, max(0, int(res.get("technical_accuracy", 75))))
            relev = min(100, max(0, int(res.get("relevance", 75))))
            comp = min(100, max(0, int(res.get("completeness", 70))))
            depth = min(100, max(0, int(res.get("depth", 70))))
            reasoning = min(100, max(0, int(res.get("reasoning", 75))))
            prob_solv = min(100, max(0, int(res.get("problem_solving", 75))))
            proj_und = min(100, max(0, int(res.get("project_understanding", 75))))
            comm = min(100, max(0, int(res.get("communication", 75))))
            struct = min(100, max(0, int(res.get("answer_structure", 75))))

            # Calculate deterministic average score for this answer
            ans_score = round(
                tech_acc * 0.35 +
                relev * 0.15 +
                comp * 0.15 +
                depth * 0.15 +
                comm * 0.10 +
                struct * 0.10
            )

            return {
                "technical_accuracy": tech_acc,
                "relevance": relev,
                "completeness": comp,
                "depth": depth,
                "reasoning": reasoning,
                "problem_solving": prob_solv,
                "project_understanding": proj_und,
                "communication": comm,
                "answer_structure": struct,
                "evaluation_confidence": min(1.0, max(0.1, float(res.get("evaluation_confidence", 0.9)))),
                "overall_score": ans_score,
                "strengths": res.get("strengths") or ["Clear technical response."],
                "weaknesses": res.get("weaknesses") or ["Could elaborate with concrete implementation metrics."],
                "missing_concepts": res.get("missing_concepts") or [],
                "factual_corrections": res.get("factual_corrections") or [],
                "evidence": res.get("evidence") or [f"Answer text: '{cleaned_answer[:100]}...'"],
                "ideal_answer_points": res.get("ideal_answer_points") or expected_points or [],
                "follow_up_needed": bool(res.get("follow_up_needed", False)),
                "answered": True
            }
        except Exception as e:
            logger.warning(f"Fallback answer evaluation triggered: {e}")
            # Fallback deterministic evaluation based on word count & basic checks
            words = cleaned_answer.split()
            word_count = len(words)
            fallback_score = min(90, max(45, 60 + min(word_count, 100) // 5))

            return {
                "technical_accuracy": fallback_score,
                "relevance": fallback_score,
                "completeness": fallback_score,
                "depth": fallback_score,
                "reasoning": fallback_score,
                "problem_solving": fallback_score,
                "project_understanding": fallback_score,
                "communication": fallback_score,
                "answer_structure": fallback_score,
                "evaluation_confidence": 0.60,
                "overall_score": fallback_score,
                "strengths": ["Answer submitted."],
                "weaknesses": ["Provide more technical specifics and trade-offs."],
                "missing_concepts": [],
                "factual_corrections": [],
                "evidence": [f"Candidate provided {word_count} words response."],
                "ideal_answer_points": expected_points or [],
                "follow_up_needed": False,
                "answered": True
            }

    def calculate_speaking_metrics(
        self,
        qna_list: List[Dict[str, Any]],
        audio_durations: Optional[List[float]] = None
    ) -> Optional[Dict[str, Any]]:
        """Calculates deterministic speaking metrics if voice mode was used."""
        has_audio = any(q.get("audio_duration", 0) > 0 or q.get("speaking_duration", 0) > 0 for q in qna_list)
        if audio_durations:
            has_audio = any(d > 0 for d in audio_durations)

        if not has_audio:
            return None

        total_words = 0
        total_fillers = 0
        total_speaking_seconds = 0.0
        total_latency_seconds = 0.0

        detected_fillers = {}

        for idx, q in enumerate(qna_list):
            ans = q.get("answer", "")
            words = re.findall(r'\b\w+\b', ans.lower())
            total_words += len(words)

            for w in words:
                if w in COMMON_FILLER_WORDS:
                    total_fillers += 1
                    detected_fillers[w] = detected_fillers.get(w, 0) + 1

            dur = q.get("audio_duration") or q.get("speaking_duration") or (audio_durations[idx] if audio_durations and idx < len(audio_durations) else 0)
            total_speaking_seconds += float(dur)
            total_latency_seconds += float(q.get("response_latency", 1.5))

        speaking_minutes = max(0.1, total_speaking_seconds / 60.0)
        wpm = round(total_words / speaking_minutes, 1)
        filler_rate = round((total_fillers / max(1, total_words)) * 100, 1)

        avg_latency = round(total_latency_seconds / max(1, len(qna_list)), 1)

        return {
            "is_voice_interview": True,
            "speaking_duration_seconds": round(total_speaking_seconds, 1),
            "words_per_minute": wpm,
            "total_words": total_words,
            "filler_word_count": total_fillers,
            "filler_rate_percent": filler_rate,
            "common_fillers": detected_fillers,
            "average_response_latency_seconds": avg_latency,
            "speech_indicators": {
                "pacing": "Normal (110-160 WPM)" if 110 <= wpm <= 160 else ("Fast (>160 WPM)" if wpm > 160 else "Deliberate (<110 WPM)"),
                "filler_usage": "Low (<3%)" if filler_rate < 3.0 else ("Moderate (3-6%)" if filler_rate <= 6.0 else "High (>6%)")
            }
        }

    def verify_project_claims(
        self,
        candidate_profile: Dict[str, Any],
        evaluations: List[Dict[str, Any]],
        qna_list: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Categorizes technology and experience claims into Verified vs Candidate Claim Only."""
        verified_techs = []
        candidate_claims_only = []

        resume_skills = set(s.lower() for s in candidate_profile.get("skills", []))
        project_techs = set()
        projects = candidate_profile.get("projects", [])
        if isinstance(projects, list):
            for p in projects:
                if isinstance(p, dict):
                    techs = p.get("technologies") or p.get("tech_stack") or []
                    if isinstance(techs, list):
                        project_techs.update(t.lower() for t in techs)

        combined_evidence_text = " ".join([q.get("answer", "") for q in qna_list]).lower()

        all_mentioned_skills = resume_skills.union(project_techs)

        for skill in all_mentioned_skills:
            if skill in combined_evidence_text:
                if skill in project_techs:
                    verified_techs.append({
                        "technology": skill.capitalize(),
                        "status": "VERIFIED",
                        "evidence": "Mentioned in candidate answer and present in submitted project background."
                    })
                else:
                    verified_techs.append({
                        "technology": skill.capitalize(),
                        "status": "VERIFIED_FROM_ANSWER",
                        "evidence": "Demonstrated during interview Q&A."
                    })
            else:
                candidate_claims_only.append({
                    "technology": skill.capitalize(),
                    "status": "NOT_VERIFIED",
                    "evidence": f"Listed in profile/resume but not assessed or discussed during this interview session."
                })

        return {
            "verified_technologies": verified_techs[:8],
            "unverified_claims": candidate_claims_only[:8]
        }

    def build_skill_matrix(
        self,
        evaluations: List[Dict[str, Any]],
        qna_list: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Builds Skill Evidence Matrix with Minimum Evidence Rule enforcement."""
        topic_groups: Dict[str, List[Dict[str, Any]]] = {}

        for idx, eval_data in enumerate(evaluations):
            cat = (qna_list[idx].get("question_type") or qna_list[idx].get("category") or "Technical").capitalize()
            if cat not in topic_groups:
                topic_groups[cat] = []
            topic_groups[cat].append(eval_data)

        matrix = []
        for topic, evals in topic_groups.items():
            q_count = len(evals)
            valid_evals = [e for e in evals if e.get("answered", True)]
            if not valid_evals:
                avg_score = 0
                strong_cnt = 0
                weak_cnt = q_count
            else:
                avg_score = round(sum(e["overall_score"] for e in valid_evals) / len(valid_evals))
                strong_cnt = sum(1 for e in valid_evals if e["overall_score"] >= 75)
                weak_cnt = sum(1 for e in valid_evals if e["overall_score"] < 65)

            # MINIMUM EVIDENCE RULE
            if q_count <= 1:
                confidence_label = "Limited evidence (Only 1 question asked)"
                conf_val = 0.50
            elif q_count == 2:
                confidence_label = "Medium evidence (2 questions asked)"
                conf_val = 0.75
            else:
                confidence_label = "High evidence (3+ questions asked)"
                conf_val = 0.92

            matrix.append({
                "skill": topic,
                "questions_tested": q_count,
                "average_score": avg_score if q_count > 0 and len(valid_evals) > 0 else None,
                "strong_answers": strong_cnt,
                "weak_answers": weak_cnt,
                "confidence_score": conf_val,
"evidence_confidence": confidence_label
            })

        return matrix

    def get_evidence_level(self, answers_submitted: int, total_questions: int = 5) -> str:
        if answers_submitted <= 0:
            return "NONE"
        elif answers_submitted == 1:
            return "LOW"
        elif answers_submitted <= 4:
            return "MEDIUM"
        else:
            return "HIGH"

    def validate_report_consistency(self, report: Dict[str, Any], answered_cnt: int) -> None:
        """HARD VALIDATION RULE: If answered_questions == 0, overall_score and all category scores MUST be None."""
        if answered_cnt == 0:
            if report.get("overall_score") is not None:
                raise ValueError(f"HARD VALIDATION ERROR: 0 answers submitted but overall_score is {report.get('overall_score')}")
            cat_scores = report.get("category_scores") or {}
            for cat, val in cat_scores.items():
                if val is not None:
                    raise ValueError(f"HARD VALIDATION ERROR: 0 answers submitted but category '{cat}' has score {val}")

    def compute_deterministic_overall_scores(
        self,
        evaluations: List[Dict[str, Any]],
        qna_list: List[Dict[str, Any]],
        speaking_metrics: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Calculates exact deterministic scores for overall performance and categories.
        EXCLUDES unassessed categories from denominator.
        """
        valid_evals = [e for e in evaluations if e.get("answered", True) and e.get("user_answer", "").strip()]
        total_questions = max(len(qna_list), len(evaluations))
        answered_questions = len(valid_evals)

        if answered_questions == 0:
            return {
                "overall_score": None,
                "technical_score": None,
                "problem_solving_score": None,
                "project_understanding_score": None,
                "role_knowledge_score": None,
                "communication_score": None,
                "coding_score": None,
                "consistency_score": None,
                "category_scores": {
                    "technical": None,
                    "problem_solving": None,
                    "project_understanding": None,
                    "role_knowledge": None,
                    "communication": None,
                    "coding": None,
                    "consistency": None
                },
                "coverage_percent": 0
            }

        # Calculate scores for tested areas
        tech_scores = [e["technical_accuracy"] for e in valid_evals if e.get("technical_accuracy") is not None]
        prob_scores = [e["problem_solving"] for e in valid_evals if e.get("problem_solving") is not None]
        proj_scores = [e["project_understanding"] for e in valid_evals if e.get("project_understanding") is not None]
        comm_scores = [e["communication"] for e in valid_evals if e.get("communication") is not None]
        role_scores = [e["relevance"] for e in valid_evals if e.get("relevance") is not None]

        cat_scores: Dict[str, Optional[int]] = {}

        cat_scores["technical"] = round(statistics.mean(tech_scores)) if tech_scores else None
        cat_scores["problem_solving"] = round(statistics.mean(prob_scores)) if prob_scores else None
        cat_scores["project_understanding"] = round(statistics.mean(proj_scores)) if proj_scores else None
        cat_scores["communication"] = round(statistics.mean(comm_scores)) if comm_scores else None
        cat_scores["role_knowledge"] = round(statistics.mean(role_scores)) if role_scores else None

        # Check if coding questions were present
        coding_evals = [evaluations[i] for i, q in enumerate(qna_list) if i < len(evaluations) and ("code" in (q.get("question_type") or "").lower() or "coding" in (q.get("category") or "").lower())]
        if coding_evals:
            c_scores = [e["overall_score"] for e in coding_evals if e.get("overall_score") is not None]
            cat_scores["coding"] = round(statistics.mean(c_scores)) if c_scores else None
        else:
            cat_scores["coding"] = None

        # Consistency score requires MINIMUM 3 answered questions
        all_ans_scores = [e["overall_score"] for e in valid_evals if e.get("overall_score") is not None]
        if len(all_ans_scores) >= 3:
            stdev = statistics.stdev(all_ans_scores)
            consistency_score = max(50, round(100 - (stdev * 1.5)))
            cat_scores["consistency"] = consistency_score
        else:
            cat_scores["consistency"] = None

        # Overall score requires MINIMUM 3 answered questions
        if answered_questions < 3:
            overall_score = None
        else:
            total_weight = 0.0
            weighted_sum = 0.0
            for cat, w in CATEGORY_WEIGHTS.items():
                val = cat_scores.get(cat)
                if val is not None:
                    total_weight += w
                    weighted_sum += val * w
            overall_score = round(weighted_sum / total_weight) if total_weight > 0 else None

        coverage_percent = round((answered_questions / max(1, total_questions)) * 100)

        return {
            "overall_score": overall_score,
            "technical_score": cat_scores["technical"],
            "problem_solving_score": cat_scores["problem_solving"],
            "project_understanding_score": cat_scores["project_understanding"],
            "role_knowledge_score": cat_scores["role_knowledge"],
            "communication_score": cat_scores["communication"],
            "coding_score": cat_scores["coding"],
            "consistency_score": cat_scores["consistency"],
            "category_scores": cat_scores,
            "coverage_percent": coverage_percent
        }

    async def generate_assessment_report(
        self,
        session_info: Dict[str, Any],
        candidate_profile: Dict[str, Any],
        qna_list: List[Dict[str, Any]],
        audio_durations: Optional[List[float]] = None
    ) -> Dict[str, Any]:
        """Main entry point for generating evidence-based interview report.
        Zero answers -> Fast NO_RESPONSE report with ZERO LLM calls.
        """
        session_id = session_info.get("session_id", "session-1")
        target_role = session_info.get("role", "Software Engineer")
        job_description = session_info.get("job_description", "")

        # Filter out empty answers
        valid_qna = [qna for qna in qna_list if qna.get("answer", "").strip()]
        answered_cnt = len(valid_qna)

        # ----------------------------------------------------
        # ZERO-ANSWER DETERMINISTIC PATH (NO LLM CALL)
        # ----------------------------------------------------
        if answered_cnt == 0:
            no_response_report = {
                "session_id": session_id,
                "status": "EXITED",
                "report_type": "NO_RESPONSE",
                "trust_label": "No Evidence",
                "evidence_level": "NONE",
                "engine_version": self.engine_version,
                "candidate": {
                    "name": candidate_profile.get("name", "Candidate"),
                    "target_role": target_role
                },
                "overall_score": None,
                "technical_score": None,
                "problem_solving_score": None,
                "project_understanding_score": None,
                "role_knowledge_score": None,
                "communication_score": None,
                "coding_score": None,
                "consistency_score": None,
                "category_scores": {
                    "technical": None,
                    "problem_solving": None,
                    "project_understanding": None,
                    "role_knowledge": None,
                    "communication": None,
                    "coding": None,
                    "consistency": None
                },
                "coverage_percent": 0,
                "completion_percentage": 0.0,
                "questions_presented": max(1, len(qna_list)),
                "questions_answered": 0,
                "questions_skipped": 0,
                "skill_evidence_matrix": [],
                "claim_verification": [],
                "speaking_metrics": None,
                "interview_summary": {
                    "overall_score": None,
                    "questions_answered": 0,
                    "questions_total": max(1, len(qna_list)),
                    "summary": "Assessment unavailable. The interview was exited before any candidate answer was submitted. No technical, communication, problem-solving, project, or role-performance scores were generated."
                },
                "recommendation": "Not Assessed",
                "final_recommendation": "No performance score was generated because no interview answers were submitted. Start a new interview to receive a meaningful performance assessment.",
                "strengths": [],
                "weaknesses": [],
                "incorrect_concepts": [],
                "missing_concepts": [],
                "question_evaluations": [],
                "question_reviews": [],
                "personalized_learning_plan": [],
                "limitations": ["Insufficient evidence — no candidate answers were submitted."]
            }
            self.validate_report_consistency(no_response_report, 0)
            return no_response_report

        # ----------------------------------------------------
        # 1. Answer-level evaluations (Only for actual answers)
        # ----------------------------------------------------
        evaluations = []
        for idx, qna in enumerate(valid_qna):
            q_text = qna.get("question", "")
            a_text = qna.get("answer", "")
            cat = qna.get("question_type") or qna.get("category") or "technical"
            diff = qna.get("difficulty", "medium")

            eval_res = await self.evaluate_single_answer(
                question=q_text,
                answer=a_text,
                category=cat,
                difficulty=diff,
                job_title=target_role,
                job_description=job_description
            )
            eval_res["user_answer"] = a_text
            evaluations.append(eval_res)

        # 2. Deterministic calculations
        speaking_metrics = self.calculate_speaking_metrics(valid_qna, audio_durations)
        deterministic_scores = self.compute_deterministic_overall_scores(evaluations, valid_qna, speaking_metrics)
        skill_matrix = self.build_skill_matrix(evaluations, valid_qna)
        claim_verification = self.verify_project_claims(candidate_profile, evaluations, valid_qna)

        evidence_hash = self.compute_evidence_hash(valid_qna)
        evidence_level = self.get_evidence_level(answered_cnt, len(qna_list))
        
        if answered_cnt >= 4 and deterministic_scores["coverage_percent"] >= 75:
            trust_label = "High Evidence"
            report_type = "FULL"
        elif answered_cnt >= 3:
            trust_label = "Medium Evidence"
            report_type = "FULL"
        else:
            trust_label = "Limited Evidence"
            report_type = "PARTIAL"

        verified_dataset = {
            "session_id": session_id,
            "trust_label": trust_label,
            "report_type": report_type,
            "evidence_snapshot_hash": evidence_hash,
            "target_role": target_role,
            "deterministic_scores": deterministic_scores,
            "skill_evidence_matrix": skill_matrix,
            "claim_verification": claim_verification,
            "speaking_metrics": speaking_metrics or "Not assessed — text mode interview",
            "evaluations_summary": [
                {
                    "question_order": idx + 1,
                    "question": valid_qna[idx].get("question"),
                    "answer": valid_qna[idx].get("answer"),
                    "score": evaluations[idx]["overall_score"],
                    "strengths": evaluations[idx]["strengths"],
                    "weaknesses": evaluations[idx]["weaknesses"],
                    "factual_corrections": evaluations[idx]["factual_corrections"]
                }
                for idx in range(len(valid_qna))
            ]
        }

        # 3. LLM Report Synthesizer (strictly explains pre-calculated numbers)
        synthesizer_prompt = get_report_synthesizer_prompt(verified_dataset)
        try:
            llm_report = await ai_service.generate_json(
                messages=[
                    {"role": "system", "content": synthesizer_prompt["system"]},
                    {"role": "user", "content": synthesizer_prompt["user"]}
                ]
            )
        except Exception as e:
            logger.error(f"Error in report synthesizer LLM: {e}")
            llm_report = {
                "executive_summary": f"Partial interview assessment based on {answered_cnt} submitted answers for {target_role}.",
                "final_recommendation": "Partial Assessment" if deterministic_scores["overall_score"] is None else ("Pass" if deterministic_scores["overall_score"] >= 75 else "Needs Practice"),
                "technical_analysis": "Evaluated technical depth for answered questions.",
                "project_analysis": "Verified candidate project claims against interview evidence.",
                "communication_analysis": "Pacing and response structure evaluated.",
                "strong_areas": ["Answered technical interview questions."],
                "weak_areas": ["Elaborate further with quantitative metrics."],
                "incorrect_concepts": [],
                "missing_concepts": [],
                "personalized_learning_plan": [
                    {"priority": 1, "topic": "Technical Depth", "action": "Practice explaining system trade-offs with concrete metrics."}
                ],
                "limitations": [f"Session evaluated with {trust_label} confidence."]
            }

        # 4. Construct Final Immutable Report Object
        question_evaluations_ui = []
        for idx, qna in enumerate(valid_qna):
            e = evaluations[idx]
            question_evaluations_ui.append({
                "question_id": f"q{idx+1}",
                "question": qna.get("question", "Question"),
                "category": qna.get("question_type") or qna.get("category") or "Technical",
                "difficulty": qna.get("difficulty", "medium"),
                "candidate_answer": qna.get("answer", "No answer recorded"),
                "score": e["overall_score"],
                "technical_accuracy": e["technical_accuracy"],
                "relevance": e["relevance"],
                "strengths": e["strengths"],
                "weaknesses": e["weaknesses"],
                "missing_concepts": e["missing_concepts"],
                "factual_corrections": e["factual_corrections"],
                "evidence": e["evidence"],
                "ideal_answer_points": e["ideal_answer_points"]
            })

        ov_score = deterministic_scores["overall_score"]

        final_report = {
            "session_id": session_id,
            "status": "PARTIAL" if report_type == "PARTIAL" else "COMPLETED",
            "report_type": report_type,
            "engine_version": self.engine_version,
            "evidence_snapshot_hash": evidence_hash,
            "trust_label": trust_label,
            "evidence_level": evidence_level,
            "prompt_versions": {
                "evaluator": ANSWER_EVALUATOR_PROMPT_VERSION,
                "synthesizer": REPORT_SYNTHESIZER_PROMPT_VERSION
            },
            "candidate": {
                "name": candidate_profile.get("name", "Candidate"),
                "target_role": target_role
            },
            # STRICT BACKEND SCORES
            "overall_score": ov_score,
            "technical_score": deterministic_scores["technical_score"],
            "problem_solving_score": deterministic_scores["problem_solving_score"],
            "project_understanding_score": deterministic_scores["project_understanding_score"],
            "role_knowledge_score": deterministic_scores["role_knowledge_score"],
            "communication_score": deterministic_scores["communication_score"],
            "coding_score": deterministic_scores["coding_score"],
            "consistency_score": deterministic_scores["consistency_score"],
            "category_scores": deterministic_scores["category_scores"],
            "coverage_percent": deterministic_scores["coverage_percent"],
            "completion_percentage": round((answered_cnt / max(1, len(qna_list))) * 100, 1),
            "questions_presented": len(qna_list),
            "questions_answered": answered_cnt,
            "questions_skipped": len(qna_list) - answered_cnt,
            # EVIDENCE MATRICES
            "skill_evidence_matrix": skill_matrix,
            "claim_verification": claim_verification,
            "speaking_metrics": speaking_metrics,
            # DETAILED REVIEW & SYNTHESIS
            "interview_summary": {
                "overall_score": ov_score,
                "questions_answered": answered_cnt,
                "questions_total": len(qna_list),
                "summary": llm_report.get("executive_summary", "")
            },
            "recommendation": "Partial Assessment" if ov_score is None else ("Pass" if ov_score >= 75 else "Needs Practice"),
            "final_recommendation": llm_report.get("final_recommendation") or ("Partial Assessment — complete more questions to get an overall score." if ov_score is None else ("Pass - Strong overall demonstration." if ov_score >= 75 else "Needs Practice - Review technical implementation details.")),
            "strengths": llm_report.get("strong_areas") or ["Answered candidate questions."],
            "weaknesses": llm_report.get("weak_areas") or ["Provide more quantitative details."],
            "incorrect_concepts": llm_report.get("incorrect_concepts") or [],
            "missing_concepts": llm_report.get("missing_concepts") or [],
            "question_evaluations": question_evaluations_ui,
            "question_reviews": question_evaluations_ui,
            "personalized_learning_plan": llm_report.get("personalized_learning_plan") or [],
            "limitations": llm_report.get("limitations") or [f"Assessment generated with {trust_label}."]
        }

        self.validate_report_consistency(final_report, answered_cnt)
        return final_report

assessment_engine = AssessmentEngine()
