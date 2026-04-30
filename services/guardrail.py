import logging

from prompts import GUARDRAIL_PROMPT
from services.gemini_client import generate_content_with_fallback
from config import settings

logger = logging.getLogger(__name__)


def is_allowed_topic(user_message: str) -> bool:
    text = (user_message or "").strip()
    if len(text) <= 15:
        return True

    try:
        prompt = GUARDRAIL_PROMPT.format(user_message=text)
        response = generate_content_with_fallback(
            model_name=settings.guardrail_model,
            content=prompt,
            temperature=0.0,
            max_tokens=10,
            request_options={"timeout": 10},
        )
        result = (response.text or "").strip().upper()
        return "ALLOWED" in result
    except Exception:
        # Fail open so transient classifier errors do not block users.
        logger.exception("Guardrail classification failed; allowing request.")
        return True
