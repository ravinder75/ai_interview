import json
import logging
import httpx
from typing import Dict, Any, List, Optional
from app.config import settings

logger = logging.getLogger(__name__)

SAFE_ERROR_MESSAGE = "AI service is temporarily unavailable. Please try again."

class AIService:
    def __init__(self):
        self.base_url = settings.AI_BASE_URL.rstrip("/")

    @property
    def api_key(self) -> str:
        return settings.OPENROUTER_API_KEY

    @property
    def model(self) -> str:
        return settings.OPENROUTER_MODEL or "google/gemini-2.0-flash-lite-001:free"

    async def generate(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> str:
        target_model = model or self.model
        key = self.api_key
        if not key or key == "sk-or-v1-placeholder":
            logger.warning("OPENROUTER_API_KEY is not configured on backend.")
            raise RuntimeError(SAFE_ERROR_MESSAGE)

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                res = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": target_model,
                        "messages": messages,
                        "temperature": temperature,
                        "max_tokens": max_tokens
                    }
                )
                if res.status_code == 200:
                    data = res.json()
                    content = data.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
                    if content:
                        logger.info("Generated AI response via OpenRouter API successfully.")
                        return content
                else:
                    logger.warning(f"OpenRouter API returned HTTP {res.status_code}")
        except Exception as ex:
            logger.error(f"OpenRouter API request failed: {type(ex).__name__}")

        raise RuntimeError(SAFE_ERROR_MESSAGE)

    async def generate_stream(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7
    ):
        """Streams AI tokens in real-time using global OPENROUTER_API_KEY."""
        key = self.api_key
        if not key or key == "sk-or-v1-placeholder":
            logger.warning("OPENROUTER_API_KEY is not configured on backend.")
            yield SAFE_ERROR_MESSAGE
            return

        target_model = model or self.model
        models_to_try = [
            target_model,
            "meta-llama/llama-3.1-8b-instruct",
            "qwen/qwen-2.5-7b-instruct"
        ]

        has_yielded = False
        for current_model in models_to_try:
            try:
                async with httpx.AsyncClient(timeout=15.0) as client:
                    async with client.stream(
                        "POST",
                        f"{self.base_url}/chat/completions",
                        headers={
                            "Authorization": f"Bearer {key}",
                            "Content-Type": "application/json"
                        },
                        json={
                            "model": current_model,
                            "messages": messages,
                            "temperature": temperature,
                            "stream": True
                        }
                    ) as response:
                        if response.status_code == 200:
                            async for line in response.aiter_lines():
                                if line.startswith("data: "):
                                    data_str = line[6:].strip()
                                    if data_str == "[DONE]":
                                        break
                                    try:
                                        chunk_json = json.loads(data_str)
                                        delta = chunk_json.get("choices", [{}])[0].get("delta", {})
                                        content = delta.get("content", "")
                                        if content:
                                            has_yielded = True
                                            yield content
                                    except Exception:
                                        pass
                            if has_yielded:
                                return
                        else:
                            logger.warning(f"OpenRouter Stream ({current_model}) returned HTTP {response.status_code}")
            except Exception as ex_stream:
                logger.warning(f"OpenRouter Stream ({current_model}) error: {type(ex_stream).__name__}")

        # Fallback to non-streaming generate if stream failed
        try:
            full_text = await self.generate(messages=messages, model=model, temperature=temperature)
            if full_text:
                words = full_text.split(" ")
                chunk_size = 4
                for i in range(0, len(words), chunk_size):
                    yield " ".join(words[i:i+chunk_size]) + " "
                return
        except Exception:
            pass

        yield SAFE_ERROR_MESSAGE

    async def generate_text(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7
    ) -> str:
        try:
            return await self.generate(messages=messages, temperature=temperature)
        except Exception as e:
            logger.error(f"generate_text exception: {type(e).__name__}")
            return SAFE_ERROR_MESSAGE

    async def generate_json(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7
    ) -> Dict[str, Any]:
        raw_text = await self.generate(messages=messages, model=model, temperature=temperature)

        clean_text = raw_text.strip()
        if clean_text.startswith("```json"):
            clean_text = clean_text[7:]
        if clean_text.startswith("```"):
            clean_text = clean_text[3:]
        if clean_text.endswith("```"):
            clean_text = clean_text[:-3]

        try:
            return json.loads(clean_text.strip())
        except json.JSONDecodeError:
            repair_messages = messages + [
                {"role": "assistant", "content": raw_text},
                {"role": "user", "content": "Your previous response was not valid JSON. Please output ONLY valid JSON matching the exact requested format, without markdown syntax or triple backticks."}
            ]
            repaired_text = await self.generate(messages=repair_messages, model=model, temperature=0.2)
            clean_repaired = repaired_text.strip()
            if clean_repaired.startswith("```json"):
                clean_repaired = clean_repaired[7:]
            if clean_repaired.startswith("```"):
                clean_repaired = clean_repaired[3:]
            if clean_repaired.endswith("```"):
                clean_repaired = clean_repaired[:-3]
            return json.loads(clean_repaired.strip())

ai_service = AIService()
