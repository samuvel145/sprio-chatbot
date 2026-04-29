# WhatsApp Plant Assistant (Twilio + Gemini)

This project is a WhatsApp chatbot for plant-health support. It supports:
- text follow-up chat for plant/agriculture questions
- image diagnosis from WhatsApp media uploads
- in-memory session context with TTL, turn limits, and rate limits
- topic guardrails to block non-plant questions

## Setup

1. Install dependencies:
   - `pip install -r requirements.txt`
2. Configure `.env`:
   - `TWILIO_ACCOUNT_SID`
   - `TWILIO_AUTH_TOKEN`
   - `GEMINI_API_KEY`

Optional tuning in `.env`:
- `SESSION_TTL_MINUTES=30`
- `MAX_TURNS_PER_SESSION=10`
- `RATE_LIMIT_RPM=10`
- `MAX_IMAGE_SIZE_MB=10`
- `PORT=5000`

## Run

- Start server: `python ChatBot.py`
- Health check: `http://127.0.0.1:5000/health`
- Webhook path for Twilio: `/whatsapp`

## Twilio Forwarding URL

Use ngrok to expose local server:
- `ngrok http 5000`

Copy the HTTPS forwarding URL and set Twilio WhatsApp webhook to:
- `https://<your-ngrok-domain>/whatsapp`
