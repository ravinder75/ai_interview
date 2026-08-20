import pytest
from app.prompts.interview_bit import get_interview_bit_prompt
from app.services.profile_normalizer import deduplicate_items

def test_interview_bit_prompt_rules():
    profile = {
        "name": "Ravinder Kama",
        "target_role": "AI/ML Engineer",
        "experience_level": "Fresher",
        "skills": ["Python", "PyTorch", "YOLOv8", "FastAPI"],
        "experience": [
            {
                "company": "MirrorWebs Technologies",
                "role": "AI Developer Intern",
                "responsibilities": ["Built AI surveillance platform with real-time object detection and ANPR using YOLOv8, FastAPI, Vue.js, PostgreSQL, and Docker"]
            }
        ]
    }
    prompt = get_interview_bit_prompt(profile)
    assert "Candidate Registered Profile & Scanned Resume Context:" in prompt
    assert "PERSONAL / HR" in prompt
    assert "PROJECT / EXPERIENCE" in prompt
    assert "TECHNICAL & DOMAIN ACCURACY" in prompt
    assert "CORE RULE" in prompt

def test_experience_deduplication():
    raw_exp = [
        {"company": "MirrorWebs Technologies", "role": "AI Developer Intern"},
        {"company": "MirrorWebs Technologies", "role": "AI Developer Intern"},
        "AI Developer Intern at MirrorWebs Technologies",
        "AI Developer Intern at MirrorWebs Technologies"
    ]
    deduped = deduplicate_items(raw_exp)
    assert len(deduped) == 2
