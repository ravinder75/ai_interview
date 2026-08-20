def get_job_analysis_prompt(job_title: str, company: str, job_text: str) -> str:
    return f"""Analyze the job description for '{job_title}' at '{company}':
\"\"\"{job_text[:4000]}\"\"\"

Extract required skills, preferred skills, core responsibilities, keywords, likely interview topics, and a step-by-step prep plan. Return JSON."""
