def get_resume_analysis_prompt(resume_text: str) -> str:
    return f"""Analyze the candidate resume text below:
\"\"\"{resume_text[:4000]}\"\"\"

Extract skills, experience summary, key strengths, missing skills for senior roles, potential interview questions, and key preparation topics. Return JSON."""
