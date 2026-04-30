import logging
import google.generativeai as genai
from config import settings

logger = logging.getLogger(__name__)

def build_model(model_name: str, temperature: float = 0.4, max_tokens: int = 1024):
    return genai.GenerativeModel(
        model_name=model_name,
        generation_config={
            "temperature": temperature,
            "max_output_tokens": max_tokens,
        },
    )


def generate_content_with_fallback(
    model_name: str,
    content,
    temperature: float = 0.4,
    max_tokens: int = 1024,
    request_options=None,
):
    api_keys = settings.gemini_api_keys
    if not api_keys:
        raise ValueError("Missing Gemini API key configuration.")

    last_error = None
    for index, api_key in enumerate(api_keys, start=1):
        try:
            genai.configure(api_key=api_key)
            model = build_model(model_name=model_name, temperature=temperature, max_tokens=max_tokens)
            return model.generate_content(content, request_options=request_options)
        except Exception as err:
            last_error = err
            masked = f"...{api_key[-4:]}" if len(api_key) >= 4 else "***"
            logger.warning(
                "Gemini request failed on key %s (%d/%d), trying next key.",
                masked,
                index,
                len(api_keys),
            )
            continue

    raise last_error
