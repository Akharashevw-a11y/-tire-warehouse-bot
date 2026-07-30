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
            await update.message.reply_photo(
                photo=tire["photo"],
                caption=text,
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        else:
            await update.message.reply_text(
                text,
                reply_markup=InlineKeyboardMarkup(keyboard)
            )


async def add(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ Нет доступа.")
        return

    try:
        brand = context.args[0]
        size = context.args[1]
        tire_type = context.args[2]
        quantity = int(context.args[3])
        price = int(context.args[4])

        context.user_data["new_tire"] = {
            "brand": brand,
            "size": size,
            "type": tire_type,
            "quantity": quantity,
            "price": price
        }

        await update.message.reply_text(
            "📸 Отправьте фотографию шины."
        )

    except:
        await update.message.reply_text(
            "Пример:\n/add Michelin 315/80R22.5 рулевая 4 28000"
        )


async def save_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_user.id != ADMIN_ID:
        return

    if "new_tire" not in context.user_data:
        return

    photo = update.message.photo[-1].file_id

    tire = context.user_data["new_tire"]

    add_tire(
        tire["brand"],
        tire["size"],
        tire["type"],
        tire["quantity"],
        tire["price"],
        photo
    )

    del context.user_data["new_tire"]

    await update.message.reply_photo(
        photo=photo,
        caption=(
            "✅ Шина добавлена!\n\n"
            f"📦 {tire['brand']}\n"
            f"📏 Размер: {tire['size']}\n"
            f"🛞 {tire['type']}\n"
            f"📦 {tire['quantity']} шт.\n"
            f"💰 {tire['price']} руб."
        )
    )


async def remove(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ Нет доступа.")
        return

    try:
        brand = context.args[0]
        size = context.args[1]
        tire_type = context.args[2]
        quantity = int(context.args[3])

        if remove_tire(brand, size, tire_type, quantity):
            await update.message.reply_text(
                "🗑️ Шина удалена."
            )
        else:
            await update.message.reply_text(
                "❌ Шина не найдена."
            )

    except:
        await update.message.reply_text(
            "Пример:\n/remove Michelin 315/80R22.5 рулевая 1"
        )


async def find(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not context.args:
        await update.message.reply_text(
            "Пример:\n/find 315/80R22.5 рулевая"
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
            f"📏 Размер: {tire['size']}\n"
            f"🛞 Назначение: {tire.get('type','')}\n"
            f"📦 Количество: {tire['quantity']} шт.\n"
            f"💰 Цена: {tire.get('price',0)} руб."
        )

        if tire.get("photo"):
            await update.message.reply_photo(
                photo=tire["photo"],
                caption=text
            )
        else:
            await update.message.reply_text(text)



async def report(update: Update, context: ContextTypes.DEFAULT_TYPE):

    tires = get_stock()

    if not tires:
        text = "📦 Склад пока пуст."

    else:
        total = 0
        money = 0

        for tire in tires:
            total += tire["quantity"]
            money += tire["quantity"] * tire.get("price", 0)

        text = (
            "📊 Отчёт склада\n\n"
            f"Всего шин: {total} шт.\n"
            f"💰 Стоимость склада: {money} руб."
        )


    if update.callback_query:
        await update.callback_query.message.reply_text(text)
    else:
        await update.message.reply_text(text)
