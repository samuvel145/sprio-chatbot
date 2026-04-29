import google.generativeai as genai
from config import settings


genai.configure(api_key=settings.gemini_api_key)


def build_model(model_name: str, temperature: float = 0.4, max_tokens: int = 1024):
    return genai.GenerativeModel(
        model_name=model_name,
        generation_config={
            "temperature": temperature,
            "max_output_tokens": max_tokens,
        },
    )
