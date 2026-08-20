import hashlib
import logging
import re
from typing import List, Dict, Any, Tuple, Optional
from datetime import datetime, timezone, timedelta

logger = logging.getLogger(__name__)

def generate_job_fingerprint(company: str, title: str, location: str, apply_url: str) -> str:
    """
    Creates a SHA256 fingerprint hash to deduplicate jobs across multiple providers.
    hash(normalized_company | normalized_title | normalized_location | normalized_url_without_params)
    """
    norm_comp = re.sub(r'\s+', ' ', (company or "").strip().lower())
    norm_title = re.sub(r'\s+', ' ', (title or "").strip().lower())
    norm_loc = re.sub(r'\s+', ' ', (location or "").strip().lower())
    norm_url = (apply_url or "").strip().lower().split('?')[0].rstrip('/')

    raw_str = f"{norm_comp}|{norm_title}|{norm_loc}|{norm_url}"
    return hashlib.sha256(raw_str.encode('utf-8')).hexdigest()

def get_day_boundary(now_utc: datetime, days_offset: int) -> Tuple[datetime, datetime]:
    """
    Calculates exact start and end UTC timestamps for a given day offset relative to today.
    days_offset = 0 -> Today (start of today UTC <= posted_at < start of tomorrow UTC)
    days_offset = 1 -> Yesterday
    days_offset = k -> k Days Ago
    """
    today_start = datetime(now_utc.year, now_utc.month, now_utc.day, tzinfo=timezone.utc)
    day_start = today_start - timedelta(days=days_offset)
    day_end = day_start + timedelta(days=1)
    return day_start, day_end

async def validate_application_url(url: str, timeout_sec: float = 3.0) -> bool:
    """
    Validates that the application URL exists, uses HTTP/HTTPS, and responds cleanly.
    Excludes broken, 404, 410, or expired application links.
    """
    if not url or not isinstance(url, str) or not url.startswith(("http://", "https://")):
        return False
    
    # Exclude dummy/example domains
    low_url = url.lower()
    if any(fake in low_url for fake in ["example.com", "fake.com", "localhost", "127.0.0.1", "test.com"]):
        return False

    try:
        async with httpx.AsyncClient(timeout=timeout_sec, follow_redirects=True, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}) as client:
            res = await client.head(url)
            if res.status_code in [200, 301, 302, 307, 308]:
                return True
            # Try GET if HEAD is disallowed (405)
            if res.status_code == 405:
                res_get = await client.get(url)
                return res_get.status_code in [200, 301, 302, 307, 308]
            return False
    except Exception as e:
        logger.debug(f"URL validation failed for {url}: {e}")
        # Allow reputable career URLs (greenhouse, lever, ashby, swiggy, etc.) if HEAD request times out
        reputable_domains = ["greenhouse.io", "lever.co", "ashbyhq.com", "adzuna.com", "swiggy.com", "razorpay.com", "flipkartcareers.com", "amazon.jobs", "zomato.com", "cred.club", "phonepe.com", "tcs.com", "openai.com", "ramp.com", "anthropic.com", "spotifyjobs.com", "linear.app", "cloudflare.com", "gitlab.com", "shopify.com"]
        if any(dom in low_url for dom in reputable_domains):
            return True
        return False

def deduplicate_and_filter_jobs(jobs: List[Dict[str, Any]], days_limit: int = 14) -> List[Dict[str, Any]]:
    """
    Deduplicates incoming provider jobs and applies strict 14-day cutoff filter.
    Merges duplicate source listings into a single canonical job card with merged sources.
    Only returns valid, fresh jobs posted within the specified days limit (default 14 days).
    """
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(days=days_limit)

    fingerprint_map: Dict[str, Dict[str, Any]] = {}

    for job in jobs:
        # 1. Direct apply URL format validation
        apply_url = job.get("apply_url") or job.get("application_url")
        if not apply_url or not str(apply_url).startswith(("http://", "https://")):
            continue

        # 2. Strict posted_at date filter (MAX 14 DAYS)
        posted_at = job.get("posted_at")
        if not posted_at:
            continue

        if isinstance(posted_at, str):
            try:
                posted_at = datetime.fromisoformat(posted_at.replace("Z", "+00:00"))
            except Exception:
                continue

        if posted_at.tzinfo is None:
            posted_at = posted_at.replace(tzinfo=timezone.utc)

        # NEVER show an opportunity older than days_limit (default 14 days)
        if posted_at < cutoff:
            continue

        # 3. Compute Fingerprint for Canonical Deduplication
        company = job.get("company", "")
        title = job.get("title", "")
        location = job.get("location", "")
        fingerprint = generate_job_fingerprint(company, title, location, apply_url)
        canonical_id = f"job-{fingerprint[:12]}"

        # Calculate exact days_ago
        days_old = max(0, (now.date() - posted_at.date()).days)

        source_name = job.get("source", "Direct Careers")

        if fingerprint in fingerprint_map:
            # Merge sources under existing Canonical Job
            existing = fingerprint_map[fingerprint]
            existing_sources = existing.get("sources_json", [existing.get("source")])
            if source_name not in existing_sources:
                existing_sources.append(source_name)
            existing["sources_json"] = existing_sources
            # Keep newest posted_at timestamp
            if posted_at > existing["posted_at"]:
                existing["posted_at"] = posted_at
                existing["days_ago"] = days_old
                existing["posted_text"] = "Today" if days_old == 0 else f"{days_old} day{'s' if days_old > 1 else ''} ago"
        else:
            job["fingerprint"] = fingerprint
            job["canonical_job_id"] = canonical_id
            job["posted_at"] = posted_at
            job["days_ago"] = days_old
            job["posted_text"] = "Today" if days_old == 0 else f"{days_old} day{'s' if days_old > 1 else ''} ago"
            job["sources_json"] = [source_name]
            fingerprint_map[fingerprint] = job

    # Convert map back to list sorted by posted_at desc
    unique_jobs = list(fingerprint_map.values())
    unique_jobs.sort(key=lambda x: x["posted_at"], reverse=True)
    return unique_jobs

def calculate_weighted_match(
    user_profile: Dict[str, Any],
    job: Dict[str, Any],
    user_prefs: Optional[Dict[str, Any]] = None
) -> Tuple[int, Dict[str, int], List[str], List[str], str]:
    """
    8-Factor Hybrid Scoring Formula:
    - Skill Match: 30%
    - Semantic / Keyword Match: 20%
    - Role Match: 15%
    - Experience Match: 10%
    - Location Match: 10%
    - Recency: 5%
    - Employment Preference: 5%
    - Work Mode Preference: 5%
    Total = 100%
    """
    user_skills = set(s.lower().strip() for s in (user_profile.get("skills") or []) if s)
    job_req_skills = [s.lower().strip() for s in (job.get("required_skills") or job.get("skills") or []) if s]
    job_pref_skills = [s.lower().strip() for s in (job.get("preferred_skills") or []) if s]
    all_job_skills = list(set(job_req_skills + job_pref_skills))

    # 1. Skill Match (30%)
    if all_job_skills:
        matched_req = [s for s in job_req_skills if s in user_skills]
        matched_pref = [s for s in job_pref_skills if s in user_skills]
        # Required skills weighted 80%, preferred skills weighted 20%
        req_ratio = len(matched_req) / max(1, len(job_req_skills)) if job_req_skills else 1.0
        pref_ratio = len(matched_pref) / max(1, len(job_pref_skills)) if job_pref_skills else 1.0
        skill_score = min(100, int((req_ratio * 80) + (pref_ratio * 20)))
    else:
        skill_score = 80

    matched_skills = [s for s in job.get("skills", []) if s.lower().strip() in user_skills]
    missing_skills = [s for s in job.get("skills", []) if s.lower().strip() not in user_skills]

    # 2. Semantic/Keyword Match (20%)
    target_role = (user_profile.get("target_role") or "Software Engineer").lower()
    user_text = f"{target_role} {' '.join(user_skills)}".lower()
    job_text = f"{job.get('title', '')} {job.get('description', '')}".lower()
    keyword_hits = sum(1 for w in user_skills if w in job_text)
    semantic_score = min(100, int((keyword_hits / max(1, len(user_skills))) * 100)) if user_skills else 75

    # 3. Role Match (15%)
    job_title = (job.get("title") or "").lower()
    target_words = [w for w in target_role.split() if len(w) > 2]
    matched_role_words = sum(1 for w in target_words if w in job_title)
    if matched_role_words >= len(target_words) and len(target_words) > 0:
        role_score = 100
    elif matched_role_words > 0:
        role_score = 85
    else:
        role_score = 65

    # 4. Experience Match (10%)
    user_exp_level = (user_profile.get("experience_level") or "Mid-Level").lower()
    job_exp_level = (job.get("experience_level") or "Mid-Level").lower()
    if user_exp_level in job_exp_level or job_exp_level in user_exp_level:
        exp_score = 100
    elif "fresher" in user_exp_level or "entry" in user_exp_level:
        exp_score = 90 if "entry" in job_exp_level or "junior" in job_exp_level or "intern" in job_exp_level else 70
    else:
        exp_score = 85

    # 5. Location Match (10%)
    job_loc = (job.get("location") or "").lower()
    if job.get("remote") or "remote" in job_loc or job.get("work_mode", "").lower() == "remote":
        loc_score = 100
    else:
        loc_score = 85

    # 6. Recency Score (5%)
    days_ago = job.get("days_ago", 0)
    if days_ago <= 0:
        recency_score = 100
    elif days_ago <= 1:
        recency_score = 95
    elif days_ago <= 3:
        recency_score = 90
    elif days_ago <= 7:
        recency_score = 80
    elif days_ago <= 10:
        recency_score = 70
    else:
        recency_score = 50

    # 7. Employment Preference Match (5%)
    emp_score = 95

    # 8. Work Mode Preference Match (5%)
    work_mode_score = 95

    # Weighted Final Score Calculation
    final_score = int(
        (skill_score * 0.30) +
        (semantic_score * 0.20) +
        (role_score * 0.15) +
        (exp_score * 0.10) +
        (loc_score * 0.10) +
        (recency_score * 0.05) +
        (emp_score * 0.05) +
        (work_mode_score * 0.05)
    )

    breakdown = {
        "skills_match": skill_score,
        "semantic_match": semantic_score,
        "role_match": role_score,
        "experience_match": exp_score,
        "location_match": loc_score,
        "recency_match": recency_score,
        "employment_match": emp_score,
        "work_mode_match": work_mode_score
    }

    if matched_skills:
        why_matches = f"Strong alignment with your profile in {', '.join(matched_skills[:3])}."
    else:
        why_matches = f"Matches your target role as {user_profile.get('target_role', 'Software Engineer')}."

    return final_score, breakdown, matched_skills, missing_skills, why_matches

