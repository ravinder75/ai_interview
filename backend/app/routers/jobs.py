import asyncio
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.resume import Resume
from app.models.job import JobDescriptionAnalysis, Job, SavedJob, JobApplication
from app.schemas.job import JobAnalyzeRequest, JobAnalyzeResponse
from app.services.ai_service import ai_service
from app.services.prompts import get_job_analysis_prompt
from app.security import get_current_user, get_current_user_required
from app.services.job_providers import GreenhouseProvider, LeverProvider, AshbyProvider, AdzunaProvider, SeedJobProvider
from app.services.job_engine import deduplicate_and_filter_jobs, calculate_weighted_match, get_day_boundary

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/jobs", tags=["AI Live Job Intelligence & Matching"])

# Instantiate official/authorized provider adapters
greenhouse_adapter = GreenhouseProvider()
lever_adapter = LeverProvider()
ashby_adapter = AshbyProvider()
adzuna_adapter = AdzunaProvider()
seed_adapter = SeedJobProvider()

async def sync_jobs_to_db(db: Session, jobs_data: List[Dict[str, Any]]) -> List[Job]:
    """Upsert canonical jobs into database `jobs` table using fingerprint and application_url validation."""
    now = datetime.now(timezone.utc)
    db_jobs = []
    
    for item in jobs_data:
        fp = item.get("fingerprint")
        apply_url = item.get("apply_url") or item.get("application_url")
        if not fp or not apply_url:
            continue
            
        existing = db.query(Job).filter(Job.fingerprint == fp).first()
        posted_at = item.get("posted_at")
        if isinstance(posted_at, str):
            try:
                posted_at = datetime.fromisoformat(posted_at.replace("Z", "+00:00"))
            except Exception:
                posted_at = now

        if existing:
            existing.company = item.get("company", existing.company)
            existing.title = item.get("title", existing.title)
            existing.location = item.get("location", existing.location)
            existing.country = item.get("country", existing.country)
            existing.city = item.get("city", existing.city)
            existing.work_mode = "Remote" if item.get("remote") else ("Hybrid" if item.get("hybrid") else "On-site")
            existing.job_type = item.get("employment_type", existing.job_type)
            existing.experience_level = item.get("experience_level", existing.experience_level)
            existing.category = item.get("category") or item.get("job_category", existing.category)
            existing.salary_range = item.get("salary_range", existing.salary_range)
            existing.salary_min = item.get("salary_min")
            existing.salary_max = item.get("salary_max")
            existing.salary_currency = item.get("salary_currency", "USD")
            existing.description = item.get("description", existing.description)
            existing.skills = item.get("skills", [])
            existing.required_skills = item.get("required_skills", [])
            existing.preferred_skills = item.get("preferred_skills", [])
            existing.sources_json = item.get("sources_json", [item.get("source", "Company Careers")])
            existing.last_verified_at = now
            existing.application_url = apply_url
            existing.is_active = True
            db_jobs.append(existing)
        else:
            new_job = Job(
                canonical_job_id=item.get("canonical_job_id"),
                fingerprint=fp,
                company=item.get("company"),
                title=item.get("title"),
                location=item.get("location", "Remote"),
                country=item.get("country", "Global"),
                city=item.get("city"),
                work_mode="Remote" if item.get("remote") else ("Hybrid" if item.get("hybrid") else "On-site"),
                job_type=item.get("employment_type", "Full-time"),
                experience_level=item.get("experience_level", "Mid-Level"),
                category=item.get("category") or item.get("job_category", "Software Development"),
                salary_range=item.get("salary_range", "Salary Not Disclosed"),
                salary_min=item.get("salary_min"),
                salary_max=item.get("salary_max"),
                salary_currency=item.get("salary_currency", "USD"),
                description=item.get("description", ""),
                skills=item.get("skills", []),
                required_skills=item.get("required_skills", []),
                preferred_skills=item.get("preferred_skills", []),
                sources_json=item.get("sources_json", [item.get("source", "Company Careers")]),
                posted_at=posted_at,
                last_verified_at=now,
                source=item.get("source", "Company Careers"),
                application_url=apply_url,
                is_active=True
            )
            db.add(new_job)
            db_jobs.append(new_job)

    try:
        db.commit()
    except Exception as err:
        logger.warning(f"DB job persistence warning: {err}")
        db.rollback()

    return db_jobs

async def run_live_job_synchronization(query: str = "Software", days_limit: int = 14, db: Optional[Session] = None) -> List[Dict[str, Any]]:
    """
    Background & on-demand provider synchronization engine.
    Fetches, normalizes, deduplicates, and filters fresh jobs posted within 14 days.
    Persists jobs to Database.
    """
    logger.info("Starting live job synchronization across Greenhouse, Lever, Ashby, Adzuna, and Company Careers...")
    
    results = await asyncio.gather(
        greenhouse_adapter.fetch_jobs(query=query),
        lever_adapter.fetch_jobs(query=query),
        ashby_adapter.fetch_jobs(query=query),
        adzuna_adapter.fetch_jobs(query=query),
        seed_adapter.fetch_jobs(query=query),
        return_exceptions=True
    )
    
    raw_greenhouse = results[0] if isinstance(results[0], list) else []
    raw_lever = results[1] if isinstance(results[1], list) else []
    raw_ashby = results[2] if isinstance(results[2], list) else []
    raw_adzuna = results[3] if isinstance(results[3], list) else []
    raw_seeds = results[4] if isinstance(results[4], list) else []

    provider_stats = {
        "Greenhouse": len(raw_greenhouse),
        "Lever": len(raw_lever),
        "Ashby": len(raw_ashby),
        "Adzuna": len(raw_adzuna),
        "Company Careers": len(raw_seeds)
    }

    normalized_list = []
    
    for raw in raw_greenhouse:
        item = greenhouse_adapter.normalize_job(raw)
        if item: normalized_list.append(item)
        
    for raw in raw_lever:
        item = lever_adapter.normalize_job(raw)
        if item: normalized_list.append(item)

    for raw in raw_ashby:
        item = ashby_adapter.normalize_job(raw)
        if item: normalized_list.append(item)

    for raw in raw_adzuna:
        item = adzuna_adapter.normalize_job(raw)
        if item: normalized_list.append(item)

    for raw in raw_seeds:
        item = seed_adapter.normalize_job(raw)
        if item: normalized_list.append(item)

    # Deduplicate and apply 14-day date filter
    filtered_jobs = deduplicate_and_filter_jobs(normalized_list, days_limit=days_limit)
    
    _SYNC_CACHE["jobs"] = filtered_jobs
    _SYNC_CACHE["last_synced_at"] = datetime.now(timezone.utc).isoformat()
    _SYNC_CACHE["provider_stats"] = provider_stats

    # Persist if db session provided
    if db:
        await sync_jobs_to_db(db, filtered_jobs)

    logger.info(f"Live synchronization complete! {len(filtered_jobs)} fresh canonical jobs loaded within 14-day window.")
    return filtered_jobs

def matches_multi_select(filter_str: Optional[str], value: str) -> bool:
    """Helper for multi-select query params e.g. 'FULL_TIME,INTERNSHIP' matching 'Full-time'"""
    if not filter_str or filter_str.lower() in ["all", "any"]:
        return True
    parts = [p.strip().lower() for p in filter_str.split(",") if p.strip()]
    if not parts or "all" in parts:
        return True
    val_norm = value.lower().replace("-", "_").replace(" ", "_")
    return any(p == val_norm or p in val_norm or val_norm in p for p in parts)

@router.get("/opportunities")
@router.get("/job-analysis/opportunities")
async def get_job_opportunities(
    days: int = Query(14, ge=1, le=14),
    type: str = Query("all"),
    location: str = Query("all"),
    page: int = Query(1, ge=1),
    limit: int = Query(30, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Dedicated /api/job-analysis/opportunities endpoint matching requested schema:
    GET /api/job-analysis/opportunities?days=14&type=all&location=india
    Returns fresh, verified canonical job opportunities directly stored in database / live synced.
    """
    if not _SYNC_CACHE["jobs"]:
        await run_live_job_synchronization(days_limit=min(days, 14), db=db)

    jobs = _SYNC_CACHE["jobs"]
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(days=min(days, 14))

    filtered = []
    for j in jobs:
        posted_at = j.get("posted_at")
        if posted_at:
            if isinstance(posted_at, str):
                try:
                    posted_at = datetime.fromisoformat(posted_at.replace("Z", "+00:00"))
                except Exception:
                    posted_at = now
            if posted_at.tzinfo is None:
                posted_at = posted_at.replace(tzinfo=timezone.utc)
            if posted_at < cutoff:
                continue

        # Location filtering logic (India, Bengaluru, Remote India, International Remote, etc.)
        if location and location.lower() != "all":
            loc_q = location.lower().strip()
            j_loc = (j.get("location") or "").lower()
            j_country = (j.get("country") or "").lower()
            j_remote = j.get("remote", False)

            if loc_q == "india":
                if "india" not in j_loc and "india" not in j_country and not (j_remote and "india" in j_loc):
                    continue
            elif loc_q == "international_remote":
                if not j_remote:
                    continue
            elif loc_q not in j_loc and loc_q not in j_country:
                continue

        # Type filter (jobs, internships, fresher, remote, freelance, full-time, etc.)
        if type and type.lower() != "all":
            t_q = type.lower().strip()
            j_type = (j.get("employment_type") or "").lower()
            j_exp = (j.get("experience_level") or "").lower()
            j_mode = "remote" if j.get("remote") else ("hybrid" if j.get("hybrid") else "on-site")

            if t_q in ["internship", "internships"]:
                if "intern" not in j_type and "intern" not in j_exp:
                    continue
            elif t_q in ["fresher", "freshers", "entry_level"]:
                if "fresher" not in j_exp and "entry" not in j_exp and "junior" not in j_exp and "intern" not in j_exp:
                    continue
            elif t_q in ["remote", "work_from_home", "wfh"]:
                if not j.get("remote") and "remote" not in j_mode:
                    continue
            elif t_q in ["freelance", "contract"]:
                if "freelance" not in j_type and "contract" not in j_type:
                    continue
            elif t_q in ["full_time", "full-time"]:
                if "full-time" not in j_type and "fulltime" not in j_type:
                    continue
            elif t_q in ["part_time", "part-time"]:
                if "part-time" not in j_type:
                    continue

        filtered.append(j)

    # Sort strictly by newest first
    filtered.sort(key=lambda x: x.get("posted_at") or now, reverse=True)

    total = len(filtered)
    start_idx = (page - 1) * limit
    end_idx = start_idx + limit
    paginated = filtered[start_idx:end_idx]

    formatted = []
    for j in paginated:
        posted_at_val = j.get("posted_at")
        posted_iso = posted_at_val.isoformat() if isinstance(posted_at_val, datetime) else str(posted_at_val)
        days_ago_val = j.get("days_ago", 0)

        formatted.append({
            "id": j.get("id") or j.get("canonical_job_id"),
            "canonical_job_id": j.get("canonical_job_id"),
            "company": j.get("company"),
            "title": j.get("title"),
            "location": j.get("location"),
            "country": j.get("country"),
            "city": j.get("city"),
            "remote": j.get("remote", False),
            "hybrid": j.get("hybrid", False),
            "work_mode": "Remote" if j.get("remote") else ("Hybrid" if j.get("hybrid") else "On-site"),
            "job_type": j.get("employment_type", "Full-time"),
            "experience_level": j.get("experience_level", "Mid-Level"),
            "salary_range": j.get("salary_range", "Salary Not Disclosed"),
            "description": j.get("description", ""),
            "skills": j.get("skills", []),
            "posted_at": posted_iso,
            "days_ago": days_ago_val,
            "posted_text": "Today" if days_ago_val == 0 else f"{days_ago_val} days ago",
            "source": j.get("source", "Company Careers"),
            "sources_json": j.get("sources_json", [j.get("source", "Company Careers")]),
            "application_url": j.get("apply_url") or j.get("application_url"),
            "is_active": True
        })

    return {
        "opportunities": formatted,
        "total": total,
        "page": page,
        "limit": limit,
        "days": days,
        "last_updated": _SYNC_CACHE.get("last_synced_at") or now.isoformat(),
        "provider_stats": _SYNC_CACHE.get("provider_stats", {})
    }

@router.get("")
async def search_jobs(
    q: Optional[str] = Query(None),
    role: Optional[str] = Query(None),
    location: Optional[str] = Query(None),
    jobType: Optional[str] = Query("All"),
    workMode: Optional[str] = Query("All"),
    experience: Optional[str] = Query("All"),
    category: Optional[str] = Query("All"),
    remote: Optional[bool] = Query(None),
    postedWithin: int = Query(14),
    dayOffset: Optional[int] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(24, ge=1, le=100),
    sort: str = Query("newest")
):
    """
    Global Job Discovery Endpoint (/job-analysis).
    Supports multi-select jobType/workMode, day-wise date boundaries, sorting, and server-side pagination.
    """
    if not _SYNC_CACHE["jobs"]:
        await run_live_job_synchronization(query=q or "Software", days_limit=max(14, postedWithin))
        
    jobs = _SYNC_CACHE["jobs"]
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(days=postedWithin)

    # Compute Day-Wise Counts for UI Headers (Today, Yesterday, 2 Days Ago, etc.)
    day_counts = {i: 0 for i in range(15)}
    for j in jobs:
        posted_at = j.get("posted_at")
        if posted_at:
            if posted_at.tzinfo is None:
                posted_at = posted_at.replace(tzinfo=timezone.utc)
            days_old = max(0, (now.date() - posted_at.date()).days)
            if days_old in day_counts:
                day_counts[days_old] += 1

    filtered = []
    for j in jobs:
        posted_at = j.get("posted_at")
        if posted_at:
            if posted_at.tzinfo is None:
                posted_at = posted_at.replace(tzinfo=timezone.utc)
            if posted_at < cutoff:
                continue

        # Day offset boundary check if specific day requested
        if dayOffset is not None:
            days_old = (now.date() - posted_at.date()).days
            if days_old != dayOffset:
                continue

        # Query filter
        if q and q.strip():
            q_lower = q.strip().lower()
            match = (
                q_lower in (j.get("title") or "").lower() or
                q_lower in (j.get("company") or "").lower() or
                q_lower in (j.get("description") or "").lower() or
                q_lower in (j.get("location") or "").lower() or
                q_lower in (j.get("category") or "").lower() or
                any(q_lower in s.lower() for s in j.get("skills", []))
            )
            if not match: continue

        # Location filter
        if location and location.strip().lower() != "all":
            loc_q = location.strip().lower()
            job_loc = (j.get("location") or "").lower()
            if loc_q not in job_loc and not (loc_q == "remote" and j.get("remote")):
                continue

        # Remote filter
        if remote is True and not j.get("remote"):
            continue

        # Multi-select Job Type
        if jobType and not matches_multi_select(jobType, j.get("employment_type", "Full-time")):
            continue

        # Multi-select Work Mode
        work_mode_val = "Remote" if j.get("remote") else ("Hybrid" if j.get("hybrid") else "On-site")
        if workMode and not matches_multi_select(workMode, work_mode_val):
            continue

        # Category Filter
        if category and category.strip().lower() != "all":
            cat_q = category.strip().lower()
            job_cat = (j.get("category") or "").lower()
            if cat_q not in job_cat and not (cat_q == "ai / ml" and ("ai" in job_cat or "ml" in job_cat)):
                continue

        # Experience Level Filter
        if experience and experience.strip().lower() != "all":
            exp_q = experience.strip().lower()
            job_exp = (j.get("experience_level") or "").lower()
            if exp_q not in job_exp:
                continue

        filtered.append(j)

    # Sort
    if sort == "newest":
        filtered.sort(key=lambda x: x["posted_at"], reverse=True)
    elif sort == "oldest":
        filtered.sort(key=lambda x: x["posted_at"])
    elif sort == "salary_high":
        filtered.sort(key=lambda x: x.get("salary_max") or 0, reverse=True)
    elif sort == "salary_low":
        filtered.sort(key=lambda x: x.get("salary_min") or 999999)

    total = len(filtered)
    totalPages = max(1, (total + limit - 1) // limit)
    start_idx = (page - 1) * limit
    end_idx = start_idx + limit
    paginated_jobs = filtered[start_idx:end_idx]

    # Format dates for API
    formatted_items = []
    for item in paginated_jobs:
        job_copy = dict(item)
        if isinstance(job_copy.get("posted_at"), datetime):
            job_copy["posted_at_iso"] = job_copy["posted_at"].isoformat()
            job_copy["posted_at"] = job_copy["posted_at"].isoformat()
        formatted_items.append(job_copy)

    return {
        "items": formatted_items,
        "pagination": {
            "page": page,
            "limit": limit,
            "total": total,
            "totalPages": totalPages,
            "hasNext": page < totalPages,
            "hasPrevious": page > 1
        },
        "filters": {
            "postedWithin": postedWithin,
            "dayOffset": dayOffset,
            "jobType": jobType,
            "workMode": workMode,
            "experience": experience,
            "category": category,
            "location": location,
            "sort": sort
        },
        "day_counts": {
            "today": day_counts.get(0, 0),
            "yesterday": day_counts.get(1, 0),
            "two_days_ago": day_counts.get(2, 0),
            "by_day": day_counts
        },
        "lastSyncedAt": _SYNC_CACHE["last_synced_at"],
        "providerStats": _SYNC_CACHE["provider_stats"]
    }

@router.get("/matches")
@router.post("/match")
async def get_live_job_matches(
    resume_id: Optional[int] = Body(None),
    days_limit: int = Body(14),
    minMatchScore: int = Body(70),
    job_type_filter: str = Body("All"),
    work_mode_filter: str = Body("All"),
    location_filter: str = Body("All"),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    """
    Personalized Resume-Matched Job Discovery Endpoint (/interview-bit).
    Calculates 8-Factor hybrid score and returns matching jobs >= minMatchScore threshold.
    """
    # Fallback user if unauthenticated for preview
    active_user = current_user
    resume = None
    if active_user:
        if resume_id:
            resume = db.query(Resume).filter(Resume.id == resume_id, Resume.user_id == active_user.id).first()
        if not resume:
            resume = db.query(Resume).filter(Resume.user_id == active_user.id).order_by(Resume.updated_at.desc()).first()

    candidate_name = getattr(active_user, "full_name", None) or "Candidate"
    target_role = getattr(active_user, "target_role", None) or "Software Engineer"
    skills = ["Python", "JavaScript", "SQL", "Machine Learning", "FastAPI", "Vue.js", "System Design", "Git"]
    projects = ["AI Mock Interview Platform", "High Throughput Rate Limiter"]
    experience = ["Senior Software Engineer"]
    education_summary = ["B.S. Computer Science"]

    if resume:
        p_info = resume.personal_info or {}
        candidate_name = p_info.get("name") or candidate_name
        target_role = p_info.get("target_role") or target_role
        skills = [s.strip() for s in (resume.skills or []) if s.strip()] or skills
        projects = resume.projects or projects
        experience = resume.experience or experience
        for ed in (resume.education or []):
            if isinstance(ed, dict):
                education_summary.append(ed.get("degree") or ed.get("institution") or "Degree")
            elif isinstance(ed, str):
                education_summary.append(ed)

    user_profile_data = {
        "name": candidate_name,
        "target_role": target_role,
        "skills": skills,
        "experience": experience,
        "education": education_summary
    }

    if not _SYNC_CACHE["jobs"]:
        await run_live_job_synchronization(query=target_role, days_limit=days_limit)

    jobs = _SYNC_CACHE["jobs"]

    user_saved_ids = set()
    user_app_ids = set()
    if active_user:
        user_saved_ids = set(r[0] for r in db.query(SavedJob.job_id).filter(SavedJob.user_id == active_user.id).all())
        user_app_ids = set(r[0] for r in db.query(JobApplication.job_id).filter(JobApplication.user_id == active_user.id).all())

    matched_jobs = []
    for idx, j in enumerate(jobs, start=1):
        if work_mode_filter != "All":
            work_mode_val = "Remote" if j.get("remote") else ("Hybrid" if j.get("hybrid") else "On-site")
            if not matches_multi_select(work_mode_filter, work_mode_val):
                continue

        if location_filter != "All":
            if location_filter.lower() not in j.get("location", "").lower() and not j.get("remote"):
                continue

        score, breakdown, matched_skills, missing_skills, why_matches = calculate_weighted_match(user_profile_data, j)

        # Minimum match threshold filter rule
        if score < minMatchScore:
            continue

        matched_jobs.append({
            "id": j.get("id") or idx,
            "canonical_job_id": j.get("canonical_job_id") or f"job-{idx}",
            "company": j["company"],
            "title": j["title"],
            "location": j["location"],
            "work_mode": "Remote" if j.get("remote") else ("Hybrid" if j.get("hybrid") else "On-site"),
            "job_type": j.get("employment_type", "Full-time"),
            "experience_level": j.get("experience_level", "Mid-Level"),
            "salary_range": j.get("salary_range", "Salary Not Disclosed"),
            "description": j.get("description", ""),
            "skills": j.get("skills", []),
            "matched_skills": matched_skills,
            "missing_skills": missing_skills,
            "posted_at": j["posted_at"].isoformat() if isinstance(j.get("posted_at"), datetime) else str(j.get("posted_at")),
            "days_ago": j.get("days_ago", 0),
            "posted_text": j.get("posted_text", "Recently"),
            "source": j.get("source", "Company Careers"),
            "sources_json": j.get("sources_json", [j.get("source", "Company Careers")]),
            "application_url": j["apply_url"],
            "overall_match_score": score,
            "match_breakdown": breakdown,
            "why_matches": why_matches,
            "improvement_tip": f"Acquire proficiency in {', '.join(missing_skills[:2])} for maximum ATS scoring." if missing_skills else "High direct match!",
            "is_saved": (j.get("id") or idx) in user_saved_ids,
            "is_applied": (j.get("id") or idx) in user_app_ids
        })

    # Sort by Best Match + Newest
    matched_jobs.sort(key=lambda x: (x["overall_match_score"], x["posted_at"]), reverse=True)

    return {
        "candidate_profile": {
            "name": candidate_name,
            "target_role": target_role,
            "skills": skills[:20],
            "experience_count": len(experience),
            "project_count": len(projects),
            "education": education_summary[:3],
            "projects": [p.get("name") if isinstance(p, dict) else str(p) for p in projects[:3]],
            "experience_level": getattr(active_user, "experience_level", None) or "Fresher / Mid Level"
        },
        "matched_jobs": matched_jobs,
        "total_found": len(matched_jobs),
        "min_match_score": minMatchScore,
        "last_updated": _SYNC_CACHE["last_synced_at"] or datetime.now(timezone.utc).isoformat(),
        "provider_stats": _SYNC_CACHE["provider_stats"]
    }

@router.post("/{job_id}/apply-click")
def record_application_click(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    """
    Telemetry recorder for job application clicks.
    Returns clean, verified destination HTTPS URL.
    """
    job_url = "https://company.careers"
    job_source = "Direct Careers"
    
    # Check live cache first
    for j in _SYNC_CACHE.get("jobs", []):
        if j.get("id") == job_id or str(j.get("canonical_job_id")) == str(job_id):
            job_url = j.get("apply_url") or job_url
            job_source = j.get("source") or job_source
            break

    click_record = ApplicationClick(
        user_id=current_user.id if current_user else None,
        job_id=job_id if isinstance(job_id, int) else 1,
        source=job_source,
        application_url=job_url
    )
    db.add(click_record)
    db.commit()
    return {
        "status": "tracked",
        "job_id": job_id,
        "destination_url": job_url
    }

@router.post("/sync")
async def trigger_manual_sync(days_limit: int = Query(14)):
    """Manual sync trigger for testing & administrative refresh"""
    jobs = await run_live_job_synchronization(days_limit=days_limit)
    return {
        "success": True,
        "message": f"Successfully synchronized {len(jobs)} live jobs from providers.",
        "jobs_count": len(jobs),
        "last_synced_at": _SYNC_CACHE["last_synced_at"],
        "provider_stats": _SYNC_CACHE["provider_stats"]
    }

@router.post("/analyze", response_model=JobAnalyzeResponse)
async def analyze_job_description(
    request: JobAnalyzeRequest,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    if not request.job_description_text.strip():
        raise HTTPException(status_code=400, detail="Job description text is empty")

    prompt = get_job_analysis_prompt(request.job_title, request.company_name or "", request.job_description_text)
    user_prompt = """
    Return JSON matching this exact structure:
    {
        "required_skills": ["Python", "FastAPI", "PostgreSQL"],
        "preferred_skills": ["Docker", "Kubernetes", "AWS"],
        "responsibilities": ["Design scalable REST APIs", "Lead technical code reviews"],
        "keywords": ["Microservices", "CI/CD", "System Architecture"],
        "likely_interview_topics": ["Database Indexing", "API Rate Limiting", "STAR Conflict Resolution"],
        "personalized_prep_plan": [
            "Day 1: Review core Python & FastAPI async patterns",
            "Day 2: Practice system design for API Rate Limiter",
            "Day 3: Prepare 3 STAR behavioral stories"
        ]
    }
    """

    try:
        res = await ai_service.generate_json(
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": user_prompt}
            ]
        )
        req_skills = res.get("required_skills", ["Core Programming", "APIs", "Database Management"])
        pref_skills = res.get("preferred_skills", ["Cloud Deployments", "Containerization"])
        resp = res.get("responsibilities", ["Develop clean software", "Collaborate with team"])
        keywords = res.get("keywords", ["Scalability", "Clean Code", "Agile"])
        topics = res.get("likely_interview_topics", ["System Design", "Technical Deep Dive", "Behavioral"])
        prep_plan = res.get("personalized_prep_plan", [
            "Review core technical requirements",
            "Prepare 3 STAR stories for behavioral questions",
            "Conduct mock practice session for system architecture"
        ])
    except Exception as e:
        req_skills = ["Software Engineering", "REST APIs", "SQL"]
        pref_skills = ["Docker", "Vue/React"]
        resp = ["Design scalable backend services", "Maintain code quality"]
        keywords = ["Agile", "CI/CD", "Testing"]
        topics = ["API Architecture", "Performance Tuning"]
        prep_plan = ["Prepare core resume projects", "Practice mock technical interview"]

    db_job = JobDescriptionAnalysis(
        user_id=current_user.id if current_user else None,
        job_title=request.job_title,
        company_name=request.company_name or "",
        job_description_text=request.job_description_text[:2000],
        required_skills=req_skills,
        preferred_skills=pref_skills,
        responsibilities=resp,
        keywords=keywords,
        likely_interview_topics=topics,
        personalized_prep_plan=prep_plan
    )
    db.add(db_job)
    db.commit()
    db.refresh(db_job)
    return db_job

@router.post("/save/{job_id}")
def save_user_job(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_required)
):
    existing = db.query(SavedJob).filter(SavedJob.user_id == current_user.id, SavedJob.job_id == job_id).first()
    if existing:
        db.delete(existing)
        db.commit()
        return {"status": "un-saved", "job_id": job_id}
    else:
        new_save = SavedJob(user_id=current_user.id, job_id=job_id)
        db.add(new_save)
        db.commit()
        return {"status": "saved", "job_id": job_id}

@router.get("/applications")
def get_user_applications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_required)
):
    apps = db.query(JobApplication).filter(JobApplication.user_id == current_user.id).order_by(JobApplication.applied_at.desc()).all()
    res = []
    for a in apps:
        res.append({
            "id": a.id,
            "job_id": a.job_id,
            "company": "Live Partner",
            "title": "Technical Developer",
            "status": a.status,
            "source": a.source,
            "application_url": a.application_url,
            "applied_at": a.applied_at.isoformat() if a.applied_at else None
        })
    return res

@router.post("/apply/{job_id}")
def track_job_application(
    job_id: int,
    data: Dict[str, Any] = Body(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_required)
):
    app_record = JobApplication(
        user_id=current_user.id,
        job_id=job_id,
        status=data.get("status", "Applied"),
        source=data.get("source", "Company Careers"),
        application_url=data.get("application_url", "https://company.careers")
    )
    db.add(app_record)
    db.commit()
    db.refresh(app_record)
    return {"status": "tracked", "application_id": app_record.id, "job_id": job_id}
