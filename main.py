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

from handlers import stock, add, remove, find, save_photo
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
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "Привет! 👋\n\n"
        "Выберите действие:",
        reply_markup=reply_markup
    )


async def menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    if query.data == "menu_stock":
        await stock(update, context)

    elif query.data == "menu_find":
        await query.message.reply_text(
            "Введите поиск:\n/find Michelin"
        )

    elif query.data == "menu_add":

        if update.effective_user.id != ADMIN_ID:
            await query.message.reply_text(
                "❌ Нет доступа."
            )
            return

        await query.message.reply_text(
            "Пример добавления:\n/add Michelin 205 зима 4"
        )

    elif query.data == "menu_remove":

        if update.effective_user.id != ADMIN_ID:
            await query.message.reply_text(
                "❌ Нет доступа."
            )
            return

        await query.message.reply_text(
            "Пример удаления:\n/remove Michelin 205 зима 2"
        )


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_user.id != ADMIN_ID:
        await update.callback_query.answer(
            "❌ У вас нет доступа к изменению склада.",
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
        f"Размер: {tire['size']}\n"
        f"Сезон: {tire['season']}\n"
        f"Количество: {tire['quantity']} шт."
    )

    keyboard = [
        [
            InlineKeyboardButton(
                "➕",
                callback_data=f"plus_{index}"
            ),
            InlineKeyboardButton(
                "➖",
                callback_data=f"minus_{index}"
            )
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    if tire.get("photo"):
        await query.message.delete()

        await query.message.reply_photo(
            photo=tire["photo"],
            caption=text,
            reply_markup=reply_markup
        )
    else:
        await query.edit_message_text(
            text,
            reply_markup=reply_markup
        )


async def set_menu(app):

    commands = [
        BotCommand("start", "Открыть меню"),
        BotCommand("stock", "Показать склад"),
        BotCommand("find", "Поиск шин"),
        BotCommand("add", "Добавить шины"),
        BotCommand("remove", "Удалить шины")
    ]

    await app.bot.set_my_commands(commands)


def main():

    app = Application.builder().token(TOKEN).post_init(set_menu).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("stock", stock))
    app.add_handler(CommandHandler("add", add))
    app.add_handler(CommandHandler("remove", remove))
    app.add_handler(CommandHandler("find", find))

    app.add_handler(
        CallbackQueryHandler(menu_handler, pattern="^menu_")
    )

    app.add_handler(
        CallbackQueryHandler(button_handler, pattern="^(plus|minus)_")
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
