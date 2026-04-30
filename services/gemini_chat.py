import logging
from typing import Dict, List, Optional
from services.gemini_client import generate_content_with_fallback
from config import settings
from prompts import SYSTEM_PROMPT

logger = logging.getLogger(__name__)


def _build_system_prompt(last_diagnosis: Optional[Dict]) -> str:
    if not last_diagnosis:
        return SYSTEM_PROMPT

    return (
        f"{SYSTEM_PROMPT}\n\n"
        "Last diagnosis context:\n"
        f"- Plant: {last_diagnosis.get('plant', 'Unknown')}\n"
        f"- Disease: {last_diagnosis.get('disease', 'Unknown')}\n"
        f"- Confidence: {last_diagnosis.get('confidence', 'Unknown')}\n"
    )


def generate_reply(
    user_message: str,
    chat_history: List[Dict[str, str]],
    last_diagnosis: Optional[Dict] = None,
) -> str:
    system_prompt = _build_system_prompt(last_diagnosis)

    contents = [{"role": "user", "parts": [{"text": system_prompt}]}]
    for msg in chat_history:
        role = "user" if msg["role"] == "user" else "model"
        contents.append({"role": role, "parts": [{"text": msg["content"]}]})
    contents.append({"role": "user", "parts": [{"text": user_message}]})

    try:
        response = generate_content_with_fallback(
            model_name=settings.chat_model,
            content=contents,
            temperature=0.6,
            max_tokens=700,
            request_options={"timeout": 20},
        )
        text = (response.text or "").strip()
        return text or "Please try again. I could not generate a response this time."
    except Exception:
        logger.exception("Chat generation failed.")
        return (
            "I am facing a temporary issue right now. "
            "Please try again in a moment with your plant question."
        )
