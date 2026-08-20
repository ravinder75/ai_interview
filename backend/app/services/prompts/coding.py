def get_coding_analysis_prompt(problem: str, language: str, code: str) -> str:
    return f"""Evaluate candidate's code submission for coding interview.
Language: {language}
Problem Statement: {problem}
Submitted Code:
\"\"\"{code}\"\"\"

Analyze time complexity, space complexity, correctness, edge case handling, and provide AI explanation and clean refactored code. Return JSON."""
