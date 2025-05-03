import os
import json
import logging
import asyncio
import html
from quart import Quart, request
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
from openai import OpenAI

# === НАСТРОЙКИ ===
BOT_TOKEN = "7942858083:AAG1E_upeUZayYi33OfA6y9eGSyo3-dwJc4"
DEEPSEEK_API_KEY = "sk-61d183527a914cf093202e5cbf28e6bc"  # ← сюда подставь свой настоящий ключ
WEBHOOK_URL = f"https://your-app-name.onrender.com/webhook/{BOT_TOKEN}"

# === OpenAI SDK с DeepSeek API ===
client = OpenAI(
    api_key=DEEPSEEK_API_KEY,
    base_url="https://api.deepseek.com"
)

# === ИНИЦИАЛИЗАЦИЯ ===
app = Quart(__name__)
application = Application.builder().token(BOT_TOKEN).build()
logging.basicConfig(level=logging.INFO)

# === Форматирование текста для Telegram ===
def format_response_for_telegram(text: str) -> str:
    text = html.escape(text)  # Экранируем HTML-символы
    lines = text.split("\n")
    formatted = []

    in_code_block = False

    for i, line in enumerate(lines):
        stripped = line.strip()

        # Обработка блоков кода
        if stripped.startswith("") and not in_code_block:
            in_code_block = True
            formatted.append("<pre>")
        elif stripped.startswith("") and in_code_block:
            in_code_block = False
            formatted.append("</pre>")
        elif in_code_block:
            formatted.append(stripped)  # Добавляем строку внутри блока кода
        elif stripped.startswith("- ") or stripped.startswith("* "):
            # Форматирование списков
            formatted.append(f"<b>• {stripped[2:]}</b>")
        elif not stripped:
            formatted.append("")  # Пустая строка для отступа
        elif (i == 0 or (stripped.isupper() and len(stripped) < 60)):
            formatted.append(f"<b>{stripped}</b>")  # Жирный заголовок
        else:
            formatted.append(stripped)

    return "\n".join(formatted)

# === DeepSeek вызов ===
async def call_deepseek_stream(prompt: str) -> str:
    try:
        response = await asyncio.to_thread(
            lambda: client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt}
                ],
                stream=False
            )
        )
        return response.choices[0].message.content
    except Exception as e:
        logging.error(f"DeepSeek API error: {e}")
        return "Не удалось получить ответ от DeepSeek."

# === ХЕНДЛЕРЫ ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Напиши мне что-нибудь, и я отвечу с помощью DeepSeek.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    reply = await call_deepseek_stream(user_message)
    formatted_reply = format_response_for_telegram(reply)
    await update.message.reply_text(formatted_reply, parse_mode="HTML")

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
