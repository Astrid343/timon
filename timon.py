import os
import html
import logging
import asyncio
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
DEEPSEEK_API_KEY = "sk-61d183527a914cf093202e5cbf28e6bc"  # ← замени на свой реальный ключ
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

# === Форматирование текста ===
def format_response_for_telegram(text: str) -> str:
    text = html.escape(text)  # экранируем <, >, &
    lines = text.split('\n')
    result = []
    in_code_block = False

    for line in lines:
        if line.strip().startswith("```") and not in_code_block:
            result.append("<pre>")
            in_code_block = True
        elif line.strip().startswith("```") and in_code_block:
            result.append("</pre>")
            in_code_block = False
        elif in_code_block:
            result.append(line)
        elif line.startswith("**") and line.endswith("**"):
            result.append(f"<b>{line[2:-2]}</b>")
        elif line.startswith("* ") or line.startswith("- "):
            result.append(f"<b>• {line[2:]}</b>")
        else:
            result.append(line)

    return '\n'.join(result)

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
    welcome_message = (
        "<b>👋 Привет! Я Timon — ИИ-бот, созданный для помощи и веселья!</b>\n\n"
        "🤖 Я работаю на базе <b>DeepSeek AI</b>, поэтому могу:\n"
        "• 📚 Объяснять сложные вещи простым языком\n"
        "• 💡 Давать советы и идеи\n"
        "• ✍️ Писать тексты, код, шутки и многое другое\n\n"
        "👨‍💻 Создатель: <b>твой крутой разработчик</b>\n"
        "📩 Просто напиши мне — и я постараюсь удивить тебя ответом!"
    )
    await update.message.reply_text(welcome_message, parse_mode="HTML")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    reply = await call_deepseek_stream(user_message)
    formatted_reply = format_response_for_telegram(reply)
    await update.message.reply_text(formatted_reply, parse_mode="HTML")

application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# === ВЕБХУК ===
f"/webhook/{BOT_TOKEN}"
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
