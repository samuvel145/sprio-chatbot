import requests
from config import settings


def download_twilio_media(media_url: str) -> bytes:
    response = requests.get(
        media_url,
        auth=(settings.twilio_account_sid, settings.twilio_auth_token),
        timeout=20,
    )
    response.raise_for_status()
    return response.content
