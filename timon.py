
import logging
import openai
from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import Application, CommandHandler, CallbackContext

# Replace these values with your own credentials
BOT_TOKEN = "7942858083:AAG1E_upeUZayYi33OfA6y9eGSyo3-dwJc4"
OPENAI_API_KEY = "sk-ijklmnopqrstuvwxijklmnopqrstuvwxijklmnop"
WEBHOOK_URL = "https://timon-sgzp.onrender.com/webhook"

# Set up OpenAI API
openai.api_key = OPENAI_API_KEY

# Set up the Flask app and the Telegram bot application
app = Flask(__name__)
telegram_app = Application.builder().token(BOT_TOKEN).build()

# Set up logging
logging.basicConfig(level=logging.INFO)

# Command handler function
async def start(update: Update, context: CallbackContext):
    await update.message.reply_text("Привет! Я бот, использующий OpenAI для общения.")

# OpenAI query handler
async def handle_message(update: Update, context: CallbackContext):
    user_message = update.message.text
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=user_message,
        max_tokens=100
    )
    await update.message.reply_text(response.choices[0].text.strip())

# Set up command and message handlers
telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(MessageHandler(None, handle_message))

@app.before_first_request
def set_webhook():
    telegram_app.bot.set_webhook(WEBHOOK_URL)

@app.route("/webhook", methods=["POST"])
def webhook():
    json_str = request.get_data().decode("UTF-8")
    update = Update.de_json(json_str, telegram_app.bot)
    telegram_app.process_update(update)
    return "OK"

if __name__ == "__main__":
    import asyncio

    async def main():
        await telegram_app.bot.set_webhook(WEBHOOK_URL)
        print("Webhook установлен.")
        app.run(host="0.0.0.0", port=10000)

    asyncio.run(main())
