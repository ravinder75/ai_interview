from pydantic import BaseModel
from typing import Optional

class AppSettingsUpdateRequest(BaseModel):
    response_style: Optional[str] = "Professional"
    difficulty: Optional[str] = "Medium"
    speech_recognition: Optional[str] = "Web Speech API"
    theme: Optional[str] = "Dark"
    data_retention_days: Optional[int] = 30

class AppSettingsResponse(BaseModel):
    app_name: str
    ai_provider: str = "Omniroute OpenAI Compatible"
    ai_model: str
    response_style: str = "Professional"
    difficulty: str = "Medium"
    speech_recognition: str = "Web Speech API"
    theme: str = "Dark"
    data_retention_days: int = 30
    api_key_configured: bool = True # Never returns raw API key string
