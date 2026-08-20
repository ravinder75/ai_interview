from fastapi import APIRouter
from app.config import settings
from app.schemas.settings import AppSettingsResponse, AppSettingsUpdateRequest

router = APIRouter(prefix="/api/settings", tags=["Application Settings"])

# In-memory settings state override for user preferences
USER_SETTINGS = {
    "response_style": "Professional",
    "difficulty": "Medium",
    "speech_recognition": "Web Speech API",
    "theme": "Dark",
    "data_retention_days": 30
}

@router.get("", response_model=AppSettingsResponse)
def get_settings():
    return AppSettingsResponse(
        app_name=settings.APP_NAME,
        ai_provider="OpenRouter AI",
        ai_model=settings.OPENROUTER_MODEL,
        response_style=USER_SETTINGS["response_style"],
        difficulty=USER_SETTINGS["difficulty"],
        speech_recognition=USER_SETTINGS["speech_recognition"],
        theme=USER_SETTINGS["theme"],
        data_retention_days=USER_SETTINGS["data_retention_days"],
        api_key_configured=bool(settings.OPENROUTER_API_KEY and settings.OPENROUTER_API_KEY != "sk-or-v1-placeholder")
    )

@router.put("", response_model=AppSettingsResponse)
def update_settings(update_req: AppSettingsUpdateRequest):
    if update_req.response_style:
        USER_SETTINGS["response_style"] = update_req.response_style
    if update_req.difficulty:
        USER_SETTINGS["difficulty"] = update_req.difficulty
    if update_req.speech_recognition:
        USER_SETTINGS["speech_recognition"] = update_req.speech_recognition
    if update_req.theme:
        USER_SETTINGS["theme"] = update_req.theme
    if update_req.data_retention_days is not None:
        USER_SETTINGS["data_retention_days"] = update_req.data_retention_days

    return get_settings()
