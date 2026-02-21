# ========== Importing Libraries ==========
from flask import Flask, request, Response # Web server for webhooks
from twilio.rest import Client # Whatsapp Client
from twilio.twiml.messaging_response import MessagingResponse # Replying to Twilio servers
import ollama # LLM management
import os
from dotenv import load_dotenv
# =========================================



# ============ Set up ==========
# Load environment variables
load_dotenv()

# Twilio Client Setup
twilio_account_sid = os.getenv('TWILIO_ACCOUNT_SID')
twilio_auth_token = os.getenv('TWILIO_AUTH_TOKEN')
twilio_client = Client(twilio_account_sid, twilio_auth_token)

# Ollama Setup
model = "qwen2.5:1.5b"
system_prompt = '''
    You are a helpful assistant.
'''

# conversation_context example data:
# conversation_context = {
#   phone_num_1 : [{role, message}, {role, message}, etc...],
#   phone_num_2 : [{role, message}, {role, message}, etc...]
#   etc...
# }
conversation_context = {}
conversation_context_limit = 6

# Flask Setup
flask_app = Flask(__name__)
# ==============================



# ============ Helper Functions ============
# Stores user and LLM messages for history purposes. The caller has to specify if message is
# from the user or LLM
def store_chat(number, message, role):
    if number in conversation_context:
        cur_chat = conversation_context[number]

        if len(cur_chat) >= conversation_context_limit:
            cur_chat.pop(0)
        
        cur_chat.append({"role": role, "content": message})
    else:
        conversation_context[number] = [{"role": role, "content": message}]

# Return a list of the entire chat
def get_chat(number):
    return conversation_context[number]
# ==========================================



# ============ Flask App Routes ============
# Incoming Whatsapp messages
@flask_app.route('/whatsapp', methods=["POST"])
def whatsapp_response_route():

    # Get user details
    reply_number = request.form.get("From")
    message = request.form.get("Body")

    # Store user message
    store_chat(reply_number, message, "user")

    # Generate LLM response
    response = ollama.chat(
        model=model,
        messages=[{"role": "system", "content": system_prompt}] + get_chat(reply_number)
    )

    # Store LLM message
    store_chat(reply_number, response.message.content, "assistant")

    # Reply to the user on WhatsApp
    resp = MessagingResponse()
    resp.message(response.message.content)
    return str(resp)


# Run the application
flask_app.run(host="0.0.0.0", port=5000)
# ==========================================