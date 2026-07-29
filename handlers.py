from telegram import Update
from telegram.ext import ContextTypes
from database import add_tire, get_stock, remove_tire


async def stock(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tires = get_stock()

    if not tires:
        await update.message.reply_text("📦 Склад пока пуст.")
        return

    text = "📦 Склад шин:\n\n"

    for i, tire in enumerate(tires, start=1):
        text += (
            f"{i}. {tire['brand']}\n"
            f"Размер: {tire['size']}\n"
            f"Сезон: {tire['season']}\n"
            f"Количество: {tire['quantity']} шт.\n\n"
        )

    await update.message.reply_text(text)



async def add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        brand = context.args[0]
        size = context.args[1]
        season = context.args[2]
        quantity = int(context.args[3])

        add_tire(brand, size, season, quantity)

        await update.message.reply_text("✅ Шины добавлены на склад!")

    except:
        await update.message.reply_text(
            "Пример:\n/add Michelin 225/45R17 зима 4"
        )


async def remove(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        brand = context.args[0]
        size = context.args[1]
        season = context.args[2]
        quantity = int(context.args[3])

        if remove_tire(brand, size, season, quantity):
            await update.message.reply_text("🗑️ Шины удалены со склада!")
        else:
            await update.message.reply_text("❌ Такие шины не найдены.")

    except:
        await update.message.reply_text(
            "Пример:\n/remove Michelin 225/45R17 зима 2"
        )
