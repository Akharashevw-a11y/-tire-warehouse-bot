import os

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)

from handlers import (
    stock,
    add,
    save_photo,
    remove,
    find,
    report
)

from database import get_stock, save_stock
from config import ADMIN_ID


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = (
        "👋 Добро пожаловать в бот склада шин!\n\n"
        "Команды:\n"
        "/stock — показать склад\n"
        "/add — добавить шину\n"
        "/remove — убрать шину\n"
        "/find — поиск\n"
        "/report — отчёт"
    )

    await update.message.reply_text(text)


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_user.id != ADMIN_ID:
        await update.callback_query.answer(
            "❌ Нет доступа.",
            show_alert=True
        )
        return

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

    text = (
        f"📦 {tire['brand']}\n"
        f"📏 Размер: {tire['size']}\n"
        f"🛞 Назначение: {tire.get('type','')}\n"
        f"📦 Количество: {tire['quantity']} шт.\n"
        f"💰 Цена: {tire.get('price',0)} руб."
    )

    from telegram import InlineKeyboardButton, InlineKeyboardMarkup

    keyboard = [[
        InlineKeyboardButton("➕", callback_data=f"plus_{index}"),
        InlineKeyboardButton("➖", callback_data=f"minus_{index}")
    ]]

    markup = InlineKeyboardMarkup(keyboard)

    try:
        if tire.get("photo"):
            await query.edit_message_caption(
                caption=text,
                reply_markup=markup
            )
        else:
            await query.edit_message_text(
                text=text,
                reply_markup=markup
            )
    except:
        pass


def main():

    token = os.getenv("TOKEN")

    if not token:
        print("TOKEN не найден")
        return

    app = Application.builder().token(token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("stock", stock))
    app.add_handler(CommandHandler("add", add))
    app.add_handler(CommandHandler("remove", remove))
    app.add_handler(CommandHandler("find", find))
    app.add_handler(CommandHandler("report", report))

    app.add_handler(
        MessageHandler(
            filters.PHOTO,
            save_photo
        )
    )

    app.add_handler(
        CallbackQueryHandler(button_handler)
    )

    print("Бот запущен")

    app.run_polling()


if __name__ == "__main__":
    main()
