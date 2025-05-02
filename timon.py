import os
import logging
import openai
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters

# API tokens
TELEGRAM_API_TOKEN = "7942858083:AAG1E_upeUZayYi33OfA6y9eGSyo3-dwJc4"
OPENAI_API_KEY = "sk-5678ijklmnopabcd5678ijklmnopabcd5678ijkl"

# Flask app setup
app = Flask(__name__)

# Set OpenAI API key
openai.api_key = OPENAI_API_KEY

# Set up logging
logging.basicConfig(level=logging.INFO)

# Function to handle /start command
async def start(update: Update, context):
    await update.message.reply_text("Hello! Send me a message and I will reply with GPT-3's response.")

# Function to handle incoming messages
async def handle_message(update: Update, context):
    user_message = update.message.text

    # Call OpenAI API to get a response
    try:
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=user_message,
            max_tokens=150
        )
        await update.message.reply_text(response.choices[0].text.strip())
    except Exception as e:
        await update.message.reply_text("Error: Could not process your request.")
        logging.error(f"Error: {e}")

# Flask route to handle webhooks
@app.route(f"/webhook/{TELEGRAM_API_TOKEN}", methods=["POST"])
async def webhook(request):
    payload = await request.get_json()
    update = Update.de_json(payload, None)
    application = Application.builder().token(TELEGRAM_API_TOKEN).build()
    await application.process_update(update)
    return "", 200

# Run Flask app
if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
