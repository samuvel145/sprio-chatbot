from typing import Dict, List, Optional
from services.gemini_client import build_model
from config import settings
from prompts import SYSTEM_PROMPT


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
    model = build_model(settings.chat_model, temperature=0.6, max_tokens=700)

    contents = [{"role": "user", "parts": [{"text": system_prompt}]}]
    for msg in chat_history:
        role = "user" if msg["role"] == "user" else "model"
        contents.append({"role": role, "parts": [{"text": msg["content"]}]})
    contents.append({"role": "user", "parts": [{"text": user_message}]})

    response = model.generate_content(contents, request_options={"timeout": 20})
    text = (response.text or "").strip()
    return text or "Please try again. I could not generate a response this time."
