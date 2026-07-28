import os
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

TOKEN = os.getenv("TOKEN")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🚗 Добро пожаловать в бот склада шин!\n\n"
        "Доступные команды:\n"
        "/stock — показать склад\n"
        "/add — добавить шины\n"
        "/remove — удалить шины"
    )


async def stock(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📦 Склад пока пуст."
    )


async def add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "➕ Функция добавления шин будет подключена следующим шагом."
    )


async def remove(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "➖ Функция удаления шин будет подключена следующим шагом."
    )


def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("stock", stock))
    app.add_handler(CommandHandler("add", add))
    app.add_handler(CommandHandler("remove", remove))

    print("Бот запущен...")
    app.run_polling()


if __name__ == "__main__":
    main()
