import pytest
from datetime import datetime, timezone, timedelta
from app.services.job_engine import generate_job_fingerprint, deduplicate_and_filter_jobs, calculate_weighted_match, get_day_boundary

def test_generate_job_fingerprint_consistency():
    fp1 = generate_job_fingerprint("OpenAI", "Machine Learning Engineer", "San Francisco, CA", "https://openai.com/careers/mle?utm_source=adzuna")
    fp2 = generate_job_fingerprint("  openai ", "machine learning engineer", "san francisco, ca", "https://openai.com/careers/mle")
    assert fp1 == fp2

def test_deduplicate_and_filter_jobs_14_day_cutoff():
    now = datetime.now(timezone.utc)
    jobs = [
        {
            "title": "ML Engineer",
            "company": "OpenAI",
            "location": "Remote",
            "apply_url": "https://openai.com/job1",
            "posted_at": now - timedelta(days=2),
            "source": "Ashby"
        },
        {
            "title": "ML Engineer",
            "company": "OpenAI",
            "location": "Remote",
            "apply_url": "https://openai.com/job1",
            "posted_at": now - timedelta(days=1), # Duplicate listing from Greenhouse, newer timestamp
            "source": "Greenhouse"
        },
        {
            "title": "Old Architect",
            "company": "LegacyCorp",
            "location": "Remote",
            "apply_url": "https://legacy.com/oldjob",
            "posted_at": now - timedelta(days=16), # Excluded (>14 days)
            "source": "Direct"
        }
    ]

    filtered = deduplicate_and_filter_jobs(jobs, days_limit=14)

    assert len(filtered) == 1
    canonical_job = filtered[0]
    assert canonical_job["company"] == "OpenAI"
    assert "Ashby" in canonical_job["sources_json"]
    assert "Greenhouse" in canonical_job["sources_json"]
    assert canonical_job["days_ago"] <= 2

def test_calculate_weighted_match_8_factors():
    user_profile = {
        "name": "Alex Candidate",
        "target_role": "Machine Learning Engineer",
        "skills": ["Python", "PyTorch", "CUDA", "LLMs", "FastAPI", "Docker"],
        "experience_level": "Mid Level"
    }

    job = {
        "title": "Machine Learning Engineer",
        "company": "OpenAI",
        "location": "San Francisco, CA",
        "work_mode": "Hybrid",
        "employment_type": "Full-time",
        "experience_level": "Mid Level",
        "required_skills": ["Python", "PyTorch", "CUDA"],
        "preferred_skills": ["LLMs", "Kubernetes"],
        "skills": ["Python", "PyTorch", "CUDA", "LLMs", "Kubernetes"],
        "days_ago": 0,
        "remote": False
    }

    score, breakdown, matched, missing, why = calculate_weighted_match(user_profile, job)

    assert score >= 75
    assert "Python" in matched
    assert "PyTorch" in matched
    assert "Kubernetes" in missing
    assert "skills_match" in breakdown
    assert "role_match" in breakdown
    assert "OpenAI" in why or "Python" in why or "Machine Learning" in why

def test_day_boundary_calculator():
    now_utc = datetime(2026, 8, 19, 14, 30, tzinfo=timezone.utc)
    day_start, day_end = get_day_boundary(now_utc, days_offset=0) # Today
    assert day_start == datetime(2026, 8, 19, 0, 0, tzinfo=timezone.utc)
    assert day_end == datetime(2026, 8, 20, 0, 0, tzinfo=timezone.utc)
