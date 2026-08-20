def get_behavioral_prompt(question: str, answer: str) -> str:
    return f"""Evaluate this behavioral interview answer using the STAR method (Situation, Task, Action, Result).
Question: {question}
Answer: {answer}

Provide individual ratings (1-10) for Situation, Task, Action, and Result, along with constructive advice to improve the weakest STAR section."""
