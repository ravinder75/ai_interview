import os
import re
import uuid
import tempfile
import logging
from typing import Dict, Any, List, Optional
from pypdf import PdfReader
from docx import Document
from app.services.ai_service import ai_service

logger = logging.getLogger(__name__)

MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024 # 10 MB

def extract_resume_text(file_bytes: bytes, filename: str) -> str:
    if len(file_bytes) > MAX_FILE_SIZE_BYTES:
        raise ValueError("File size exceeds maximum limit of 10 MB")

    ext = os.path.splitext(filename)[1].lower()
    text = ""

    if ext == ".pdf":
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            tmp.write(file_bytes)
            tmp_path = tmp.name
        try:
            # 1. Try PyPDF
            try:
                reader = PdfReader(tmp_path)
                for page in reader.pages:
                    extracted = page.extract_text()
                    if extracted:
                        text += extracted + "\n"
            except Exception as pe:
                logger.warning(f"PyPDF primary extraction warning: {pe}")

            # 2. If text is empty or failed, try pdfplumber fallback if available
            if not text.strip():
                try:
                    import pdfplumber
                    with pdfplumber.open(tmp_path) as pdf:
                        for page in pdf.pages:
                            t = page.extract_text()
                            if t:
                                text += t + "\n"
                except Exception as pl_err:
                    logger.warning(f"pdfplumber fallback warning: {pl_err}")

            # 3. Image-based OCR fallback if still empty
            if not text.strip():
                try:
                    import fitz  # PyMuPDF
                    doc = fitz.open(tmp_path)
                    for page in doc:
                        text += page.get_text() + "\n"
                except Exception:
                    pass

            if not text.strip():
                # Allow fallback raw string decoding for uncompressed text in malformed PDFs
                decoded = file_bytes.decode("latin-1", errors="ignore")
                printable = "".join([c for c in decoded if c.isprintable() or c in ["\n", "\r", "\t"]])
                if len(printable) > 10:
                    text = printable[:4000]

        except Exception as e:
            logger.error(f"PDF extraction error: {e}")
            if not text.strip():
                raise ValueError("Failed to parse PDF file. Please ensure it is a valid PDF document.")
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

    elif ext in [".docx", ".doc"]:
        with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as tmp:
            tmp.write(file_bytes)
            tmp_path = tmp.name
        try:
            doc = Document(tmp_path)
            for para in doc.paragraphs:
                if para.text:
                    text += para.text + "\n"
        except Exception as e:
            logger.warning(f"DOCX python-docx extraction failed, trying string fallback: {e}")
            decoded = file_bytes.decode("latin-1", errors="ignore")
            printable = "".join([c for c in decoded if c.isprintable() or c in ["\n", "\r", "\t"]])
            if len(printable) > 10:
                text = printable[:4000]
            else:
                raise ValueError("Failed to parse DOCX file. Please ensure it is a valid Word document.")
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

    elif ext == ".txt":
        text = file_bytes.decode("utf-8", errors="ignore")
    else:
        raise ValueError(f"Unsupported file format '{ext}'. Only PDF, DOCX, and TXT files are accepted.")

    return text.strip()

def infer_target_role(skills: List[str], text: str) -> str:
    text_lower = (text + " " + " ".join(skills)).lower()

    if any(k in text_lower for k in ["machine learning", "tensorflow", "pytorch", "yolo", "opencv", "scikit-learn", "ai/ml", "hugging face", "deep learning"]):
        return "AI/ML Engineer"
    elif any(k in text_lower for k in ["react", "vue", "angular", "css", "html5", "tailwind", "frontend"]):
        return "Frontend Developer"
    elif any(k in text_lower for k in ["devops", "kubernetes", "docker", "terraform", "ci/cd", "aws", "cloud"]):
        return "DevOps Engineer"
    elif any(k in text_lower for k in ["data science", "data engineer", "spark", "hadoop", "etl"]):
        return "Data Engineer"
    else:
        return "Backend Developer"

class ResumeService:
    async def build_candidate_profile(self, file_bytes: bytes, filename: str) -> Dict[str, Any]:
        raw_text = extract_resume_text(file_bytes, filename)
        
        prompt_system = """You are an expert resume parser. Parse the candidate resume text and extract structured JSON matching this exact structure:
{
  "name": "Candidate Name",
  "email": "candidate@example.com",
  "phone": "+1 234 567 8900",
  "target_role": "AI/ML Engineer",
  "experience_level": "Fresher",
  "skills": ["Python", "PyTorch", "TensorFlow", "FastAPI", "SQL", "OpenCV"],
  "programming_languages": ["Python", "JavaScript", "SQL"],
  "frameworks": ["PyTorch", "TensorFlow", "FastAPI", "Flask", "Vue.js"],
  "databases": ["PostgreSQL", "MongoDB", "MySQL"],
  "projects": [
    {
      "name": "IntelliRetail AI",
      "technologies": ["PyTorch", "FastAPI", "YOLOv8"],
      "description": "Smart retail analytics and object detection system."
    }
  ],
  "internships": [
    {
      "role": "AI/ML Intern",
      "company": "Tech Corp",
      "duration": "6 months",
      "description": "Developed computer vision and NLP models for automated document processing."
    }
  ],
  "experience": [
    "AI/ML Intern at Tech Corp - Built deep learning models with PyTorch and deployed FastAPI inference endpoints."
  ],
  "education": ["B.Tech Computer Science"],
  "certifications": ["Deep Learning Specialization"]
}"""

        user_msg = f"Resume Text:\n{raw_text[:5000]}"

        try:
            parsed = await ai_service.generate_json(
                messages=[
                    {"role": "system", "content": prompt_system},
                    {"role": "user", "content": user_msg}
                ]
            )
        except Exception as e:
            logger.warning(f"AI resume parsing fallback triggered: {e}")
            parsed = {}

        skills = parsed.get("skills", [])
        detected_role = parsed.get("target_role") or (infer_target_role(skills, raw_text) if raw_text else "Software Engineer")

        # Extract projects
        raw_projects = parsed.get("projects", [])
        formatted_projects = []
        for p in raw_projects:
            if isinstance(p, dict):
                formatted_projects.append({
                    "name": p.get("name", "Project"),
                    "technologies": p.get("technologies", []),
                    "description": p.get("description", "")
                })
            elif isinstance(p, str):
                formatted_projects.append({
                    "name": p,
                    "technologies": [],
                    "description": ""
                })

        # Extract internships and experience
        raw_internships = parsed.get("internships", [])
        raw_experience = parsed.get("experience", [])
        formatted_experience = []

        if raw_internships and isinstance(raw_internships, list):
            for itn in raw_internships:
                if isinstance(itn, dict):
                    comp = itn.get('company', '')
                    r = itn.get('role', 'Intern')
                    d = itn.get('description', '')
                    dur = itn.get('duration', '')
                    formatted_experience.append(f"{r}{' at ' + comp if comp else ''}{' (' + dur + ')' if dur else ''}: {d}" if d else f"{r} at {comp}")
                elif isinstance(itn, str):
                    formatted_experience.append(itn)

        if raw_experience and isinstance(raw_experience, list):
            for exp in raw_experience:
                if isinstance(exp, str) and exp not in formatted_experience:
                    formatted_experience.append(exp)
                elif isinstance(exp, dict):
                    formatted_experience.append(f"{exp.get('role', '')} at {exp.get('company', '')}: {exp.get('description', '')}")

        profile = {
            "name": parsed.get("name") or "Candidate",
            "email": parsed.get("email") or "",
            "phone": parsed.get("phone") or "",
            "target_role": detected_role,
            "experience_level": parsed.get("experience_level") or "Fresher",
            "skills": skills,
            "programming_languages": parsed.get("programming_languages") or [],
            "frameworks": parsed.get("frameworks") or [],
            "databases": parsed.get("databases") or [],
            "projects": formatted_projects,
            "internships": raw_internships,
            "experience": formatted_experience,
            "education": parsed.get("education") or [],
            "certifications": parsed.get("certifications") or []
        }

        resume_id = str(uuid.uuid4())
        return {
            "resume_id": resume_id,
            "profile": profile,
            "raw_text": raw_text[:3000]
        }

resume_service = ResumeService()
