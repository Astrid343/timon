import logging
import openai
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

# API tokens
TELEGRAM_API_TOKEN = "7942858083:AAG1E_upeUZayYi33OfA6y9eGSyo3-dwJc4"
OPENAI_API_KEY = "sk-5678ijklmnopabcd5678ijklmnopabcd5678ijkl"

# Flask app setup
app = Flask(__name__)

# Set OpenAI API key
openai.api_key = OPENAI_API_KEY

# Set up logging
logging.basicConfig(level=logging.INFO)

# Create the Telegram application globally
application = Application.builder().token(TELEGRAM_API_TOKEN).build()

# Command handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello! Send me a message and I will reply with GPT-3's response.")

# Message handler
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    try:
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=user_message,
            max_tokens=150
        )
        await update.message.reply_text(response.choices[0].text.strip())
    except Exception as e:
        logging.error(f"OpenAI error: {e}")
        await update.message.reply_text("Error: Could not process your request.")

# Register handlers
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# Flask route to handle Telegram webhook
@app.route(f"/webhook/{TELEGRAM_API_TOKEN}", methods=["POST"])
async def telegram_webhook():
    payload = await request.get_json()
    update = Update.de_json(payload, application.bot)
    await application.process_update(update)
    return "", 200

# Run Flask app
if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=10000)
