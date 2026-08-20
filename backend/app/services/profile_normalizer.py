import logging
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.interview_bit import CandidateProfile
from app.models.resume import Resume

logger = logging.getLogger(__name__)

def deduplicate_items(item_list: list) -> list:
    if not item_list:
        return []
    seen = set()
    deduped = []
    for item in item_list:
        if isinstance(item, dict):
            comp = (item.get("company") or item.get("name") or "").strip().lower()
            role = (item.get("role") or item.get("title") or "").strip().lower()
            key = f"{comp}|{role}" if (comp or role) else str(item).strip().lower()
            if key not in seen:
                seen.add(key)
                deduped.append(item)
        elif isinstance(item, str):
            cleaned = item.strip()
            key = cleaned.lower()[:80]
            if key not in seen:
                seen.add(key)
                deduped.append(cleaned)
        else:
            deduped.append(item)
    return deduped

def get_normalized_candidate_context(
    db: Session,
    current_user: Optional[User] = None,
    profile_id: Optional[str] = None
) -> Dict[str, Any]:
    profile_obj = None

    # 1. Primary priority: CandidateProfile matching current_user.id
    if current_user:
        profile_obj = db.query(CandidateProfile).filter(CandidateProfile.user_id == current_user.id).order_by(CandidateProfile.updated_at.desc(), CandidateProfile.created_at.desc()).first()

    # 2. Secondary priority: CandidateProfile matching explicit profile_id (Must belong to current_user or be anonymous)
    if not profile_obj and profile_id:
        query = db.query(CandidateProfile).filter(CandidateProfile.id == profile_id)
        if current_user:
            query = query.filter((CandidateProfile.user_id == current_user.id) | (CandidateProfile.user_id.is_(None)))
        profile_obj = query.first()

    # 3. Fetch associated Resume strictly matching current_user.id
    user_resume = None
    if current_user:
        user_resume = db.query(Resume).filter(Resume.user_id == current_user.id).order_by(Resume.is_primary.desc(), Resume.updated_at.desc()).first()
    elif profile_obj and profile_obj.user_id:
        user_resume = db.query(Resume).filter(Resume.user_id == profile_obj.user_id).order_by(Resume.is_primary.desc(), Resume.updated_at.desc()).first()

    name = "Candidate"
    target_role = "Software Engineer"
    experience_level = "Fresher"
    email = None
    location = None
    skills = []
    experience = []
    projects = []
    education = []
    certifications = []
    achievements = []
    additional_info = ""
    raw_resume_text = ""

    if profile_obj:
        name = profile_obj.name or name
        email = profile_obj.email or email
        target_role = profile_obj.target_role or target_role
        experience_level = profile_obj.experience_level or experience_level
        location = profile_obj.location or location
        skills = profile_obj.skills or []
        experience = profile_obj.experience or []
        projects = profile_obj.projects or []
        education = profile_obj.education or []
        certifications = profile_obj.certifications or []
        achievements = profile_obj.achievements or []
        additional_info = profile_obj.additional_information or ""

    if user_resume:
        p_info = user_resume.personal_info or {}
        if not name or name == "Candidate":
            name = p_info.get("name") or (current_user.name if current_user else "Candidate")
        if not target_role or target_role == "Software Engineer":
            target_role = p_info.get("target_role") or (current_user.target_role if current_user else "Software Engineer")
        
        if not skills and user_resume.skills:
            skills = user_resume.skills
        if user_resume.experience:
            experience = (experience or []) + user_resume.experience
        if not projects and user_resume.projects:
            projects = user_resume.projects
        if not education and user_resume.education:
            education = user_resume.education
        if not certifications and user_resume.certifications:
            certifications = user_resume.certifications
        if user_resume.extracted_text:
            raw_resume_text = user_resume.extracted_text

    # Deduplicate entries
    deduped_experience = deduplicate_items(experience)
    deduped_projects = deduplicate_items(projects)
    deduped_skills = deduplicate_items(skills)

    normalized_context = {
        "name": name,
        "email": email,
        "target_role": target_role,
        "experience_level": experience_level,
        "location": location,
        "skills": deduped_skills,
        "work_experience": deduped_experience,
        "experience": deduped_experience,
        "internships": deduped_experience,
        "projects": deduped_projects,
        "education": deduplicate_items(education),
        "certifications": deduplicate_items(certifications),
        "achievements": deduplicate_items(achievements),
        "additional_information": additional_info,
        "raw_resume_snippet": raw_resume_text[:1000] if raw_resume_text else ""
    }

    return normalized_context
