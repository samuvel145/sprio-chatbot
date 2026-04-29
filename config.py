import os
from dataclasses import dataclass
from dotenv import load_dotenv


load_dotenv()


@dataclass
class Settings:
    twilio_account_sid: str = os.getenv("TWILIO_ACCOUNT_SID", "")
    twilio_auth_token: str = os.getenv("TWILIO_AUTH_TOKEN", "")
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")

    host: str = os.getenv("HOST", "0.0.0.0")
    port: int = int(os.getenv("PORT", "5000"))
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"

    session_ttl_minutes: int = int(os.getenv("SESSION_TTL_MINUTES", "30"))
    max_turns_per_session: int = int(os.getenv("MAX_TURNS_PER_SESSION", "10"))
    rate_limit_rpm: int = int(os.getenv("RATE_LIMIT_RPM", "10"))
    max_image_size_mb: int = int(os.getenv("MAX_IMAGE_SIZE_MB", "10"))

    chat_model: str = os.getenv("CHAT_MODEL", "gemini-2.5-flash")
    guardrail_model: str = os.getenv("GUARDRAIL_MODEL", "gemini-2.0-flash-lite")
    vision_model: str = os.getenv("VISION_MODEL", "gemini-2.5-flash")

    @property
    def max_image_size_bytes(self) -> int:
        return self.max_image_size_mb * 1024 * 1024


settings = Settings()
