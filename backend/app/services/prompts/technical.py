def get_technical_prompt(role: str, category: str, count: int) -> str:
    return f"""Generate {count} technical interview questions for a candidate applying for {role} focusing on {category}. Include key aspects to evaluate for each question. Return JSON array."""
