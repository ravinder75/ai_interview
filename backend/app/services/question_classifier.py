import re
from typing import Dict, Any

def classify_interview_question(q: str) -> Dict[str, Any]:
    ql = q.lower().strip()
    
    if any(k in ql for k in ["tell me about yourself", "introduce yourself", "walk me through your background", "who are you"]):
        return {"category": "INTRODUCTION", "confidence": 0.98}
    elif any(k in ql for k in ["yolov8", "opencv", "computer vision", "object detection", "image segmentation", "resnet", "cnn"]):
        return {"category": "COMPUTER_VISION", "confidence": 0.96}
    elif any(k in ql for k in ["nlp", "natural language", "bert", "transformer", "llm", "tokenization", "huggingface", "embeddings"]):
        return {"category": "NLP", "confidence": 0.96}
    elif any(k in ql for k in ["deep learning", "neural network", "backpropagation", "pytorch", "tensorflow", "loss function", "gradient descent"]):
        return {"category": "DEEP_LEARNING", "confidence": 0.95}
    elif any(k in ql for k in ["machine learning", "supervised", "unsupervised", "random forest", "scikit-learn", "regression", "classification", "overfitting"]):
        return {"category": "MACHINE_LEARNING", "confidence": 0.95}
    elif any(k in ql for k in ["system design", "microservices", "load balancer", "sharding", "scalability", "rate limiter", "distributed"]):
        return {"category": "SYSTEM_DESIGN", "confidence": 0.94}
    elif any(k in ql for k in ["write a code", "write a function", "write a python", "implement", "coding", "python program"]):
        return {"category": "CODING", "confidence": 0.95}
    elif any(k in ql for k in ["linked list", "binary tree", "graph", "heap", "stack", "queue", "hash map", "array", "matrix"]):
        return {"category": "DATA_STRUCTURE", "confidence": 0.94}
    elif any(k in ql for k in ["algorithm", "binary search", "sorting", "time complexity", "space complexity", "dynamic programming", "dijkstra"]):
        return {"category": "ALGORITHM", "confidence": 0.94}
    elif any(k in ql for k in ["fastapi", "rest api", "endpoint", "graphql", "http method", "get and post", "swagger", "openapi"]):
        return {"category": "API", "confidence": 0.93}
    elif any(k in ql for k in ["sql", "postgres", "database", "indexing", "acid", "transactions", "mongodb", "redis"]):
        return {"category": "DATABASE", "confidence": 0.94}
    elif any(k in ql for k in ["docker", "kubernetes", "ci/cd", "jenkins", "terraform", "devops", "ansible"]):
        return {"category": "DEVOPS", "confidence": 0.93}
    elif any(k in ql for k in ["aws", "azure", "gcp", "cloud", "s3", "ec2", "lambda"]):
        return {"category": "CLOUD", "confidence": 0.93}
    elif any(k in ql for k in ["cybersecurity", "encryption", "jwt", "oauth", "auth", "vulnerability", "xss", "csrf", "security"]):
        return {"category": "SECURITY", "confidence": 0.93}
    elif any(k in ql for k in ["my project", "intelliretail", "key project", "project architecture", "project impact"]):
        return {"category": "PROJECT", "confidence": 0.95}
    elif any(k in ql for k in ["work experience", "previous role", "company", "internship", "job history"]):
        return {"category": "WORK_EXPERIENCE", "confidence": 0.95}
    elif any(k in ql for k in ["resume", "cv", "profile", "skills listed", "certifications"]):
        return {"category": "RESUME", "confidence": 0.95}
    elif any(k in ql for k in ["difficult problem", "conflict", "challenge", "teamwork", "mistake", "failure", "situation", "star"]):
        return {"category": "BEHAVIORAL", "confidence": 0.92}
    elif any(k in ql for k in ["why should we hire", "salary expectation", "notice period", "strengths and weaknesses", "where do you see yourself"]):
        return {"category": "HR", "confidence": 0.92}
    elif any(k in ql for k in ["explain the concept", "what is", "how does", "difference between", "definition"]):
        return {"category": "TECHNICAL_CONCEPT", "confidence": 0.90}
    elif any(k in ql for k in ["follow-up", "elaborate on that", "can you clarify", "why did you choose"]):
        return {"category": "FOLLOW_UP", "confidence": 0.90}
    elif any(k in ql for k in ["role", "responsibilities of", "ai engineer", "software engineer"]):
        return {"category": "ROLE_SPECIFIC", "confidence": 0.90}
    else:
        return {"category": "OTHER", "confidence": 0.85}
