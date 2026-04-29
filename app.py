from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from datetime import datetime

from config import settings
from prompts import GUARDRAIL_REFUSAL
from services.session_manager import SessionManager
from services.guardrail import is_allowed_topic
from services.gemini_chat import generate_reply
from services.gemini_vision import analyse_image
from utils.twilio_media import download_twilio_media


session_manager = SessionManager(
    ttl_minutes=settings.session_ttl_minutes,
    max_turns=settings.max_turns_per_session,
)


def _format_diagnosis(result: dict) -> str:
    if result.get("error") == "not_a_plant":
        return "The uploaded image does not look like a plant/leaf. Please send a clear plant photo."
    if result.get("error"):
        return "I could not analyze the image this time. Please try again with a clearer photo."

    symptoms = result.get("symptoms", [])
    treatment = result.get("treatment", [])
    confidence = result.get("confidence", "unknown")
    return (
        "Diagnosis complete:\n"
        f"Plant: {result.get('plant', 'Unknown')}\n"
        f"Disease: {result.get('disease', 'Unknown')}\n"
        f"Confidence: {confidence}\n"
        f"Symptoms: {', '.join(symptoms) if symptoms else 'Not specified'}\n"
        f"Treatment: {'; '.join(treatment) if treatment else 'Not specified'}"
    )


def create_app() -> Flask:
    flask_app = Flask(__name__)

    @flask_app.route("/health", methods=["GET"])
    def health() -> dict:
        return {"status": "ok"}

    @flask_app.route("/whatsapp", methods=["POST"])
    def whatsapp_response_route():
        reply_number = request.form.get("From", "")
        message = (request.form.get("Body") or "").strip()
        num_media = int(request.form.get("NumMedia", "0"))
        resp = MessagingResponse()

        if not reply_number:
            resp.message("Could not identify your number. Please try again.")
            return str(resp)

        session = session_manager.get_or_create(reply_number)
        if not session.check_rate_limit(settings.rate_limit_rpm):
            resp.message("Too many requests. Please wait a minute and try again.")
            return str(resp)

        try:
            if num_media > 0:
                can_analyse, retry_after_ts = session.can_analyse_image(daily_limit=3)
                if not can_analyse and retry_after_ts is not None:
                    retry_at = datetime.fromtimestamp(retry_after_ts).strftime("%Y-%m-%d %I:%M %p")
                    resp.message(
                        f"Only three image analysis requests are allowed per day. "
                        f"You can try again at {retry_at}."
                    )
                    return str(resp)

                media_url = request.form.get("MediaUrl0", "")
                media_type = request.form.get("MediaContentType0", "image/jpeg")
                image_bytes = download_twilio_media(media_url)
                if len(image_bytes) > settings.max_image_size_bytes:
                    resp.message("Image is too large. Please upload a smaller image.")
                    return str(resp)

                session.add_message("user", "[Uploaded plant image]")
                diagnosis = analyse_image(image_bytes, media_type)
                session.last_diagnosis = diagnosis
                response_text = _format_diagnosis(diagnosis)
                session.add_message("assistant", response_text)
                resp.message(response_text)
                return str(resp)

            if not message:
                resp.message("Send a text question or upload a plant image.")
                return str(resp)

            if not is_allowed_topic(message):
                session.add_message("user", message)
                session.add_message("assistant", GUARDRAIL_REFUSAL)
                resp.message(GUARDRAIL_REFUSAL)
                return str(resp)

            session.add_message("user", message)
            reply = generate_reply(
                user_message=message,
                chat_history=session.chat_history[:-1],
                last_diagnosis=session.last_diagnosis,
            )
            session.add_message("assistant", reply)
            resp.message(reply)
            return str(resp)
        except Exception:
            resp.message("Temporary error while processing your request. Please try again.")
            return str(resp)

    return flask_app
