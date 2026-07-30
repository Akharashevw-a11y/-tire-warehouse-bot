import os

from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
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

    keyboard = [
        ["📦 Склад", "🔍 Поиск"],
        ["➕ Добавить", "🗑 Удалить"],
        ["📊 Отчёт"]
    ]

    markup = ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True
    )

    await update.message.reply_text(
        "👋 Бот склада шин запущен!",
        reply_markup=markup
    )


async def menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = update.message.text

    if text == "📦 Склад":
        await stock(update, context)

    elif text == "🔍 Поиск":
        await update.message.reply_text(
            "Введите:\n/find размер или марку"
        )

    elif text == "➕ Добавить":
        await update.message.reply_text(
            "Пример:\n/add Michelin 315/80R22.5 рулевая 4 28000"
        )

    elif text == "🗑 Удалить":
        await update.message.reply_text(
            "Пример:\n/remove Michelin 315/80R22.5 рулевая 1"
        )

    elif text == "📊 Отчёт":
        await report(update, context)



async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_user.id != ADMIN_ID:
        await update.callback_query.answer(
            "Нет доступа",
            show_alert=True
        )
        return

    query = update.callback_query
    await query.answer()

    tires = get_stock()

    action, index = query.data.split("_")
    index = int(index)

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

    keyboard = [[
        InlineKeyboardButton(
            "➕",
            callback_data=f"plus_{index}"
        ),
        InlineKeyboardButton(
            "➖",
            callback_data=f"minus_{index}"
        )
    ]]

    await query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )



def main():

    token = os.getenv("TOKEN")

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


    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            menu_handler
        )
    )


    print("Бот запущен")

    app.run_polling()



if __name__ == "__main__":
    main()
