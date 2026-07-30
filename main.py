import os

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    CallbackQueryHandler,
    MessageHandler,
    filters
)

from handlers import stock, add, remove, find, save_photo, report
from database import get_stock, save_stock
from config import ADMIN_ID


TOKEN = os.getenv("TOKEN")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    keyboard = [
        [
            InlineKeyboardButton("📦 Склад", callback_data="menu_stock"),
            InlineKeyboardButton("🔍 Поиск", callback_data="menu_find")
        ],
        [
            InlineKeyboardButton("➕ Добавить", callback_data="menu_add"),
            InlineKeyboardButton("🗑 Удалить", callback_data="menu_remove")
        ],
        [
            InlineKeyboardButton("📊 Отчёт", callback_data="menu_report")
        ]
    ]

    await update.message.reply_text(
        "Привет! 👋\n\nВыберите действие:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )



async def show_stock_button(update: Update, context: ContextTypes.DEFAULT_TYPE):

    tires = get_stock()

    if not tires:
        await update.callback_query.message.reply_text(
            "📦 Склад пока пуст."
        )
        return


    for i, tire in enumerate(tires):

        keyboard = [[
            InlineKeyboardButton("➕", callback_data=f"plus_{i}"),
            InlineKeyboardButton("➖", callback_data=f"minus_{i}")
        ]]

        text = (
            f"📦 {tire['brand']}\n"
            f"📏 Размер: {tire['size']}\n"
            f"🛞 Назначение: {tire.get('type','')}\n"
            f"📦 Количество: {tire['quantity']} шт.\n"
            f"💰 Цена: {tire.get('price',0)} руб."
        )

        if tire.get("photo"):

            await update.callback_query.message.reply_photo(
                photo=tire["photo"],
                caption=text,
                reply_markup=InlineKeyboardMarkup(keyboard)
            )

        else:

            await update.callback_query.message.reply_text(
                text,
                reply_markup=InlineKeyboardMarkup(keyboard)
            )



async def menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()


    if query.data == "menu_stock":

        await show_stock_button(update, context)


    elif query.data == "menu_find":

        await query.message.reply_text(
            "🔍 Поиск:\n\n"
            "Напишите:\n"
            "/find 315/80R22.5\n"
            "/find 315/80R22.5 рулевая"
        )


    elif query.data == "menu_report":

        await report(update, context)


    elif query.data == "menu_add":

        if update.effective_user.id != ADMIN_ID:
            await query.message.reply_text("❌ Нет доступа.")
            return

        await query.message.reply_text(
            "➕ Добавление шин:\n\n"
            "Пример:\n"
            "/add Michelin 315/80R22.5 рулевая 4 28000"
        )


    elif query.data == "menu_remove":

        if update.effective_user.id != ADMIN_ID:
            await query.message.reply_text("❌ Нет доступа.")
            return

        await query.message.reply_text(
            "🗑 Удаление шин:\n\n"
            "Пример:\n"
            "/remove Michelin 315/80R22.5 рулевая 2"
        )



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


    if action == "plus":
        tires[index]["quantity"] += 1


    elif action == "minus":

        tires[index]["quantity"] -= 1

        if tires[index]["quantity"] < 0:
            tires[index]["quantity"] = 0


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
        InlineKeyboardButton("➕", callback_data=f"plus_{index}"),
        InlineKeyboardButton("➖", callback_data=f"minus_{index}")
    ]]


    await query.message.reply_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )



async def set_menu(app):

    commands = [
        BotCommand("start", "Меню"),
        BotCommand("stock", "Склад"),
        BotCommand("find", "Поиск"),
        BotCommand("add", "Добавить"),
        BotCommand("remove", "Удалить"),
        BotCommand("report", "Отчёт")
    ]

    await app.bot.set_my_commands(commands)



def main():

    app = (
        Application
        .builder()
        .token(TOKEN)
        .post_init(set_menu)
        .build()
    )


    app.add_handler(CommandHandler("start", start))

    app.add_handler(CommandHandler("stock", stock))

    app.add_handler(CommandHandler("add", add))

    app.add_handler(CommandHandler("remove", remove))

    app.add_handler(CommandHandler("find", find))

    app.add_handler(CommandHandler("report", report))


    app.add_handler(
        CallbackQueryHandler(
            menu_handler,
            pattern="^menu_"
        )
    )


    app.add_handler(
        CallbackQueryHandler(
            button_handler,
            pattern="^(plus|minus)_"
        )
    )


    app.add_handler(
        MessageHandler(
            filters.PHOTO,
            save_photo
        )
    )


    app.run_polling()



if __name__ == "__main__":
    main()
