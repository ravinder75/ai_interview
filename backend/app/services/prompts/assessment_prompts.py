import json
from typing import Dict, Any, List

ANSWER_EVALUATOR_PROMPT_VERSION = "answer-evaluator-v3"
REPORT_SYNTHESIZER_PROMPT_VERSION = "report-synthesizer-v4"

def get_answer_evaluator_prompt(
    question: str,
    answer: str,
    category: str = "technical",
    difficulty: str = "medium",
    job_title: str = "Software Engineer",
    job_description: str = "",
    expected_points: List[str] = None
) -> Dict[str, str]:
    system_prompt = f"""You are a senior AI/ML engineer, technical interviewer, and objective interview assessment engine.

You are evaluating ONE SPECIFIC CANDIDATE ANSWER to ONE INTERVIEW QUESTION.

EVALUATION RULES:
1. Evaluate ONLY the candidate's actual answer text against the question asked.
2. DO NOT reward answer length. A long rambling answer is NOT automatically good.
3. DO NOT penalize short correct answers. If a candidate gives a direct, accurate definition or solution in 1-2 sentences, score it high.
4. Evaluate technical correctness, relevance, completeness, depth, reasoning, problem solving, project understanding, communication, and answer structure independently on a 0-100 scale.
5. Identify specific EVIDENCE quotes from the candidate answer for every deduction or strength.
6. Identify factual claims: separate correct claims, incorrect claims, and unsupported/missing concepts.
7. Return ONLY valid JSON matching the exact schema below.

SCHEMA:
{{
    "technical_accuracy": 82,
    "relevance": 90,
    "completeness": 75,
    "depth": 70,
    "reasoning": 80,
    "problem_solving": 85,
    "project_understanding": 90,
    "communication": 78,
    "answer_structure": 72,
    "evaluation_confidence": 0.92,
    "strengths": ["Quoted or described evidence of correct concept..."],
    "weaknesses": ["Specific missing concept or incorrect detail..."],
    "missing_concepts": ["Concepts expected but not mentioned..."],
    "factual_corrections": [
        {{
            "incorrect_claim": "Candidate said X",
            "correct_information": "Actual correct fact Y",
            "severity": "minor|moderate|major"
        }}
    ],
    "evidence": ["Exact quote or concrete paraphrase from answer supporting score"],
    "ideal_answer_points": ["Point 1", "Point 2", "Point 3"],
    "follow_up_needed": true
}}"""

    user_prompt = f"""Evaluate this interview answer:

Target Role: {job_title}
Job Description: {job_description or "N/A"}
Question Category: {category}
Difficulty: {difficulty}
Question: {question}
Candidate Answer: {answer}
Expected Key Points: {json.dumps(expected_points or [])}

Return JSON matching the schema."""

    return {
        "system": system_prompt,
        "user": user_prompt,
        "prompt_version": ANSWER_EVALUATOR_PROMPT_VERSION
    }

def get_report_synthesizer_prompt(verified_dataset: Dict[str, Any]) -> Dict[str, str]:
    system_prompt = f"""You are a professional technical interview assessment report writer.

You are given a VERIFIED STRUCTURED ASSESSMENT DATASET that was pre-computed by a deterministic backend engine.

CRITICAL CONSTRAINTS:
1. You MUST NOT invent, recalculate, alter, upgrade, or downgrade ANY numeric scores or metrics.
2. You MUST NOT invent candidate information, achievements, technologies, answers, or missing evidence.
3. If a category is labeled "Not assessed", explicitly state "Not assessed — insufficient evidence or category not tested in session."
4. Your sole job is to EXPLAIN the verified backend measurements clearly, neutrally, and professionally.
5. Distinguish between VERIFIED FACT, CANDIDATE CLAIM, and INSUFFICIENT EVIDENCE.
6. Tone: Neutral, specific, evidence-based, constructive. No exaggerated praise, no harsh language.

Output valid JSON matching this structure:
{{
    "executive_summary": "Explanation of verified results...",
    "final_recommendation": "Pass/Needs Practice recommendation based on measured scores...",
    "technical_analysis": "Explanation of technical topic scores and evidence matrix...",
    "project_analysis": "Explanation of project claim verification...",
    "communication_analysis": "Explanation of deterministic speaking metrics...",
    "strong_areas": ["Verified strength 1 with evidence", "Verified strength 2"],
    "weak_areas": ["Verified weakness 1 with evidence", "Verified weakness 2"],
    "incorrect_concepts": ["Factual error 1 identified"],
    "missing_concepts": ["Missing topic 1"],
    "personalized_learning_plan": [
        {{
            "priority": 1,
            "topic": "Topic Name",
            "action": "Specific practice drill based on missed question"
        }}
    ],
    "limitations": ["Explicit limitations of this interview session..."]
}}"""

    user_prompt = f"""Explain the following pre-computed verified interview dataset:

{json.dumps(verified_dataset, indent=2)}

Return JSON matching the schema."""

    return {
        "system": system_prompt,
        "user": user_prompt,
        "prompt_version": REPORT_SYNTHESIZER_PROMPT_VERSION
    }
