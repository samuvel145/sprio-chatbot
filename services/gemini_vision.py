import json
import re
from typing import Dict, Optional
from services.gemini_client import generate_content_with_fallback
from config import settings
from prompts import VISION_PROMPT


def _extract_json(text: str) -> Optional[Dict]:
    if not text:
        return None
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        return None
    try:
        return json.loads(match.group(0))
    except json.JSONDecodeError:
        return None


def analyse_image(image_bytes: bytes, mime_type: str) -> Dict:
    image_part = {
        "inline_data": {
            "mime_type": mime_type,
            "data": __import__("base64").b64encode(image_bytes).decode("utf-8"),
        }
    }
    response = generate_content_with_fallback(
        model_name=settings.vision_model,
        content=[VISION_PROMPT, image_part],
        temperature=0.2,
        max_tokens=1200,
        request_options={"timeout": 30},
    )
    parsed = _extract_json(response.text or "")
    if not parsed:
        return {"error": "parse_error"}
    return parsed
