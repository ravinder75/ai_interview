import re
from typing import List, Dict, Any

TECH_DICTIONARY = {
    "javascript": "JavaScript",
    "js": "JS",
    "typescript": "TypeScript",
    "ts": "TS",
    "python": "Python",
    "react": "React.js",
    "reactjs": "React.js",
    "vue": "Vue.js",
    "vuejs": "Vue.js",
    "angular": "Angular",
    "node": "Node.js",
    "nodejs": "Node.js",
    "express": "Express.js",
    "fastapi": "FastAPI",
    "docker": "Docker",
    "kubernetes": "Kubernetes",
    "aws": "AWS",
    "postgresql": "PostgreSQL",
    "postgres": "PostgreSQL",
    "mongodb": "MongoDB",
    "mongo": "MongoDB",
    "sql": "SQL",
    "git": "Git",
    "github": "GitHub",
    "gitlab": "GitLab",
    "html": "HTML5",
    "css": "CSS3",
    "tailwind": "Tailwind CSS",
    "bootstrap": "Bootstrap",
    "graphql": "GraphQL",
    "rest": "REST API"
}

COMMON_SPELLING = {
    "experiance": "Experience",
    "expeirnce": "Experience",
    "managment": "Management",
    "mangment": "Management",
    "devlopment": "Development",
    "develpment": "Development",
    "javscript": "JavaScript",
    "progamming": "Programming",
    "implimented": "Implemented",
    "responsable": "Responsible",
    "enviroment": "Environment",
    "architechture": "Architecture",
    "maintainance": "Maintenance",
    "databasea": "Database"
}

GRAMMAR_PATTERNS = [
    (r"\bworked on developing\b", "Developed", "Use active verb 'Developed' instead of passive phrase 'worked on developing'."),
    (r"\bworked on building\b", "Built", "Use active verb 'Built' instead of 'worked on building'."),
    (r"\bwas responsible for\b", "Managed", "Use strong action verb like 'Managed' or 'Led'."),
    (r"\bhelped with\b", "Assisted in", "Use action-oriented phrase like 'Assisted in' or 'Contributed to'.")
]

def scan_resume_errors(text: str) -> List[Dict[str, Any]]:
    issues = []
    issue_id = 1

    # 1. Spelling Errors
    for word_match in re.finditer(r"\b[A-Za-z]{4,}\b", text):
        raw_word = word_match.group(0)
        lower_word = raw_word.lower()
        if lower_word in COMMON_SPELLING:
            suggested = COMMON_SPELLING[lower_word]
            issues.append({
                "id": f"err_{issue_id}",
                "type": "Spelling",
                "severity": "Critical",
                "found": raw_word,
                "suggested": suggested,
                "why": f"Found spelling error '{raw_word}'. Correct spelling is '{suggested}'.",
                "fixable": True
            })
            issue_id += 1

    # 2. Capitalization Errors
    for word_match in re.finditer(r"\b[A-Za-z0-9\.\-\#\+]+\b", text):
        raw_token = word_match.group(0)
        lower_token = raw_token.lower()
        if lower_token in TECH_DICTIONARY:
            correct_cap = TECH_DICTIONARY[lower_token]
            if raw_token != correct_cap and raw_token != correct_cap.upper():
                issues.append({
                    "id": f"err_{issue_id}",
                    "type": "Capitalization",
                    "severity": "Warning",
                    "found": raw_token,
                    "suggested": correct_cap,
                    "why": f"Industry standard capitalization for '{raw_token}' is '{correct_cap}'.",
                    "fixable": True
                })
                issue_id += 1

    # 3. Spacing Errors (Missing space after comma: e.g. "Java,Python,React")
    for comma_match in re.finditer(r"\b([A-Za-z0-9]+),([A-Za-z0-9]+)\b", text):
        found_str = comma_match.group(0)
        suggested_str = f"{comma_match.group(1)}, {comma_match.group(2)}"
        issues.append({
            "id": f"err_{issue_id}",
            "type": "Spacing",
            "severity": "Warning",
            "found": found_str,
            "suggested": suggested_str,
            "why": "Missing space after comma in list items.",
            "fixable": True
        })
        issue_id += 1

    # Unnecessary space before punctuation (e.g. "Experience ,")
    for pre_space in re.finditer(r"\b([A-Za-z0-9]+)\s+([,\.:;])", text):
        found_str = pre_space.group(0)
        suggested_str = f"{pre_space.group(1)}{pre_space.group(2)}"
        issues.append({
            "id": f"err_{issue_id}",
            "type": "Spacing",
            "severity": "Warning",
            "found": found_str,
            "suggested": suggested_str,
            "why": "Unnecessary space before punctuation mark.",
            "fixable": True
        })
        issue_id += 1

    # Duplicate spaces (e.g. "Software  Engineer")
    for dup_space in re.finditer(r"\b([A-Za-z0-9]+)[ \t]{2,}([A-Za-z0-9]+)\b", text):
        found_str = dup_space.group(0)
        suggested_str = f"{dup_space.group(1)} {dup_space.group(2)}"
        issues.append({
            "id": f"err_{issue_id}",
            "type": "Duplicate Spaces",
            "severity": "Suggestion",
            "found": found_str,
            "suggested": suggested_str,
            "why": "Multiple consecutive space characters detected.",
            "fixable": True
        })
        issue_id += 1

    # 4. Grammar / Action Verb Rules
    for pattern, replacement, reason in GRAMMAR_PATTERNS:
        for match in re.finditer(pattern, text, re.IGNORECASE):
            found_str = match.group(0)
            issues.append({
                "id": f"err_{issue_id}",
                "type": "Grammar",
                "severity": "Warning",
                "found": found_str,
                "suggested": replacement,
                "why": reason,
                "fixable": True
            })
            issue_id += 1

    # Deduplicate issues by 'found' key
    seen = set()
    unique_issues = []
    for iss in issues:
        key = (iss["type"], iss["found"])
        if key not in seen:
            seen.add(key)
            unique_issues.append(iss)

    return unique_issues

def calculate_ats_metrics(text: str, profile: Dict[str, Any], issues: List[Dict[str, Any]]) -> Dict[str, Any]:
    skills = profile.get("skills", [])
    if isinstance(skills, dict):
        skills = [item for sublist in skills.values() if isinstance(sublist, list) for item in sublist]

    projects = profile.get("projects", [])
    experience = profile.get("experience", [])
    email = profile.get("email", "")

    # Breakdown scores
    keyword_match = min(25, max(10, len(skills) * 3 + (5 if projects else 0)))
    structure_score = 20 if (skills and (projects or experience)) else 12
    exp_score = min(20, max(8, len(experience) * 5 + len(projects) * 4))
    skills_score = min(15, max(5, len(skills) * 2))
    formatting_score = 10 if len([i for i in issues if i["type"] in ["Spacing", "Duplicate Spaces"]]) == 0 else 7
    contact_score = 5 if ("@" in email or profile.get("phone")) else 2
    grammar_score = 5 if len([i for i in issues if i["type"] in ["Spelling", "Grammar"]]) == 0 else 3

    total_ats = keyword_match + structure_score + exp_score + skills_score + formatting_score + contact_score + grammar_score
    total_ats = min(98, max(55, total_ats))

    return {
        "ats_score": total_ats,
        "metrics": {
            "keyword_match": {"score": keyword_match, "max": 25},
            "structure": {"score": structure_score, "max": 20},
            "experience": {"score": exp_score, "max": 20},
            "skills": {"score": skills_score, "max": 15},
            "formatting": {"score": formatting_score, "max": 10},
            "contact_info": {"score": contact_score, "max": 5},
            "grammar": {"score": grammar_score, "max": 5}
        },
        "analytics": {
            "grammar_pct": max(70, 100 - len([i for i in issues if i["type"] == "Grammar"]) * 5),
            "spelling_pct": max(75, 100 - len([i for i in issues if i["type"] == "Spelling"]) * 10),
            "formatting_pct": max(80, 100 - len([i for i in issues if i["type"] in ["Spacing", "Duplicate Spaces"]]) * 4),
            "keyword_pct": min(100, max(60, len(skills) * 12)),
            "completeness_pct": 95 if (email and skills and projects) else 75
        }
    }
