from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import add_tire, get_stock, remove_tire, find_tires
from config import ADMIN_ID

async def stock(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tires = get_stock()

    if not tires:
        await update.message.reply_text("📦 Склад пока пуст.")
        return

    for i, tire in enumerate(tires):
        keyboard = [
            [
                InlineKeyboardButton(
                    "➕",
                    callback_data=f"plus_{i}"
                ),
                InlineKeyboardButton(
                    "➖",
                    callback_data=f"minus_{i}"
                )
            ]
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)

        text = (
            f"📦 {tire['brand']}\n"
            f"Размер: {tire['size']}\n"
            f"Сезон: {tire['season']}\n"
            f"Количество: {tire['quantity']} шт."
        )

        await update.message.reply_text(
            text,
            reply_markup=reply_markup
        )


async def add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        brand = context.args[0]
        size = context.args[1]
        season = context.args[2]
        quantity = int(context.args[3])

        add_tire(brand, size, season, quantity)

        await update.message.reply_text(
            "✅ Шины добавлены на склад!"
        )

    except:
        await update.message.reply_text(
            "Пример:\n/add Michelin 205 зима 4"
        )


async def remove(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        brand = context.args[0]
        size = context.args[1]
        season = context.args[2]
        quantity = int(context.args[3])

        if remove_tire(brand, size, season, quantity):
            await update.message.reply_text(
                "🗑️ Шины удалены со склада!"
            )
        else:
            await update.message.reply_text(
                "❌ Такие шины не найдены."
            )

    except:
        await update.message.reply_text(
            "Пример:\n/remove Michelin 205 зима 2"
        )
async def find(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text(
            "Пример:\n/find Michelin"
        )
        return

    query = " ".join(context.args)

    tires = find_tires(query)

    if not tires:
        await update.message.reply_text(
            "❌ Ничего не найдено."
        )
        return

    for tire in tires:
        text = (
            f"🔍 Найдено:\n\n"
            f"📦 {tire['brand']}\n"
            f"Размер: {tire['size']}\n"
            f"Сезон: {tire['season']}\n"
            f"Количество: {tire['quantity']} шт."
        )

        await update.message.reply_text(text)
