import json
import os

from datetime import datetime

from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

try:
    from config import TOKEN
except ImportError:
    TOKEN = os.getenv("TOKEN")


# ---------- КОНСТАНТЫ ----------

TARGET_DATE = datetime(2026, 10, 2)

days_clicks = 0
help_clicks = 0
stats_clicks = 0


# ---------- КНОПКИ ----------

days_button = KeyboardButton("📅 Сколько осталось?")
help_button = KeyboardButton("ℹ️ Помощь")
stats_button = KeyboardButton("📊 Статистика")

keyboard = [
    [days_button, help_button],
    [stats_button]
]

reply_keyboard = ReplyKeyboardMarkup(
    keyboard,
    resize_keyboard=True
)


# ---------- ФУНКЦИИ РАБОТЫ С ФАЙЛОМ ----------

def save_stats():
    global days_clicks, help_clicks, stats_clicks

    data = {
        "days_clicks": days_clicks,
        "help_clicks": help_clicks,
        "stats_clicks": stats_clicks,
    }

    with open("data.json", "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


def load_stats():
    global days_clicks, help_clicks, stats_clicks

    try:
        with open("data.json", "r", encoding="utf-8") as file:
            data = json.load(file)

        days_clicks = data["days_clicks"]
        help_clicks = data["help_clicks"]
        stats_clicks = data["stats_clicks"]

    except FileNotFoundError:
        days_clicks = 0
        help_clicks = 0
        stats_clicks = 0
        save_stats()


# ---------- ОСТАЛЬНЫЕ ФУНКЦИИ ----------

def get_countdown():
    """Возвращает текст с количеством оставшихся дней."""

    today = datetime.now()
    delta = TARGET_DATE - today

    if delta.days > 0:
        return f"До 2 октября 2026 осталось {delta.days} дней! 🎉"
    elif delta.days == 0:
        return "Сегодня тот самый день! 🎉"
    else:
        return "2 октября 2026 уже прошло."


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "День добрый!\n\n"
        "Я бот обратного отсчёта с рядом дополнительных опций!\n\n"
        "Используй команды:\n"
        "📅 /days — узнать, сколько осталось дней\n"
        "📖 /help — список всех команд\n"
        "📊 /stats — статистика бота\n\n"
        f"{get_countdown()}"
    )

    await update.message.reply_text(
        text,
        reply_markup=reply_keyboard
    )


async def days_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global days_clicks

    days_clicks += 1
    save_stats()

    text = get_countdown()
    await update.message.reply_text(text)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global help_clicks

    help_clicks += 1
    save_stats()

    text = (
        "Доступные команды:\n\n"
        "/start - приветствие\n"
        "/days - узнать, сколько осталось дней\n"
        "/help - показать список команд\n"
        "/stats - статистика"
    )

    await update.message.reply_text(text)


async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global stats_clicks

    stats_clicks += 1
    save_stats()

    text = (
        "📊 Статистика бота\n\n"
        f"📅 Запросов количества дней: {days_clicks}\n"
        f"ℹ️ Просмотров помощи: {help_clicks}\n"
        f"📊 Просмотров статистики: {stats_clicks}"
    )

    await update.message.reply_text(text)


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "📅 Сколько осталось?":
        await days_command(update, context)

    elif text == "ℹ️ Помощь":
        await help_command(update, context)

    elif text == "📊 Статистика":
        await stats_command(update, context)


# ---------- ЗАПУСК ----------

def main():
    load_stats()

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("days", days_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("stats", stats_command))

    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            button_handler
        )
    )

    print("Бот запущен!")

    app.run_polling()


if __name__ == "__main__":
    main()