import os
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    CallbackQueryHandler
)

from handlers import stock, add, remove
from database import get_stock, save_stock


TOKEN = os.getenv("TOKEN")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! 👋\n\n"
        "Доступные команды:\n"
        "/stock — показать склад\n"
        "/add — добавить шины\n"
        "/remove — удалить шины"
    )


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    tires = get_stock()

    if not tires:
        return

    action, index = query.data.split("_")
    index = int(index)

    if index >= len(tires):
        return

    if action == "plus":
        tires[index]["quantity"] += 1

    elif action == "minus":
        if tires[index]["quantity"] > 0:
            tires[index]["quantity"] -= 1

    save_stock(tires)

    tire = tires[index]

    await query.edit_message_text(
        f"📦 {tire['brand']}\n"
        f"Размер: {tire['size']}\n"
        f"Сезон: {tire['season']}\n"
        f"Количество: {tire['quantity']} шт."
    )


def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("stock", stock))
    app.add_handler(CommandHandler("add", add))
    app.add_handler(CommandHandler("remove", remove))

    app.add_handler(
        CallbackQueryHandler(button_handler)
    )

    app.run_polling()


if __name__ == "__main__":
    main()
