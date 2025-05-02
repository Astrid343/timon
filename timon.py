import os
import json
import logging
import asyncio
import httpx
from quart import Quart, request
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# === НАСТРОЙКИ ===
BOT_TOKEN = "7942858083:AAG1E_upeUZayYi33OfA6y9eGSyo3-dwJc4"
OPENROUTER_API_KEY = "sk-or-vv-795ff3514ba20dbe87eb45c90c18643e262a3df9e1c61fbe80e05d95f3ba0215"
MODEL = "deepseek/deepseek-r1"
WEBHOOK_URL = f"https://your-app-name.onrender.com/webhook/{BOT_TOKEN}"

# === ИНИЦИАЛИЗАЦИЯ ===
app = Quart(__name__)
application = Application.builder().token(BOT_TOKEN).build()
logging.basicConfig(level=logging.INFO)


def process_content(content: str) -> str:
    return content.replace('<think>', '').replace('</think>', '')


async def call_deepseek_stream(prompt: str) -> str:
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "stream": True
    }

    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            async with client.stream(
                "POST",
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=payload
            ) as response:

                if response.status_code != 200:
                    text = await response.aread()
                    logging.error(f"Stream error: {response.status_code} - {text}")
                    return "Ошибка при подключении к DeepSeek API."

                full_response = []
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        line = line[6:]
                    if not line.strip():
                        continue
                    try:
                        chunk = json.loads(line)
                        delta = chunk["choices"][0]["delta"]
                        content = delta.get("content", "")
                        if content:
                            full_response.append(process_content(content))
                    except Exception as e:
                        logging.warning(f"Ошибка в разборе chunk: {e}")
                        continue

                return "".join(full_response)

        except Exception as e:
            logging.error(f"Exception during streaming: {e}")
            return "Не удалось получить ответ от DeepSeek."


# === ХЕНДЛЕРЫ ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Напиши мне что-нибудь, и я отвечу с помощью DeepSeek-R1.")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    reply = await call_deepseek_stream(user_message)
    await update.message.reply_text(reply)


application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))


# === ВЕБХУК ===
@app.post(f"/webhook/{BOT_TOKEN}")
async def webhook():
    try:
        data = await request.get_json()
        update = Update.de_json(data, application.bot)
        await application.process_update(update)
    except Exception as e:
        logging.error(f"Exception in webhook: {e}")
    return "", 200


# === MAIN ===
async def main():
    await application.initialize()
    await application.start()
    await application.bot.set_webhook(url=WEBHOOK_URL)

    from hypercorn.asyncio import serve
    from hypercorn.config import Config
    config = Config()
    config.bind = [f"0.0.0.0:{os.environ.get('PORT', '10000')}"]
    await serve(app, config)

if __name__ == "__main__":
    asyncio.run(main())
