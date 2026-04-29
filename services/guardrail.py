from prompts import GUARDRAIL_PROMPT
from services.gemini_client import build_model
from config import settings


def is_allowed_topic(user_message: str) -> bool:
    text = (user_message or "").strip()
    if len(text) <= 15:
        return True

    model = build_model(settings.guardrail_model, temperature=0.0, max_tokens=10)
    prompt = GUARDRAIL_PROMPT.format(user_message=text)
    response = model.generate_content(prompt, request_options={"timeout": 10})
    result = (response.text or "").strip().upper()
    return "ALLOWED" in result
