def get_interviewer_system_prompt(role: str, experience_level: str, interview_type: str) -> str:
    return f"""You are an expert tech recruiter and hiring manager conducting an interview for a {experience_level} {role} ({interview_type} focus).
Generate challenging, clear, and relevant interview questions. Return ONLY valid JSON format matching the requested schema."""
