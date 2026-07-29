from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import add_tire, get_stock, remove_tire, find_tires
from config import ADMIN_ID


async def stock(update: Update, context: ContextTypes.DEFAULT_TYPE):

    tires = get_stock()

    if not tires:
        await update.message.reply_text(
            "📦 Склад пока пуст."
        )
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


        if tire.get("photo"):

            await update.message.reply_photo(
                photo=tire["photo"],
                caption=text,
                reply_markup=reply_markup
            )

        else:

            await update.message.reply_text(
                text,
                reply_markup=reply_markup
            )



async def add(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_user.id != ADMIN_ID:

        await update.message.reply_text(
            "❌ У вас нет доступа."
        )
        return


    try:

        brand = context.args[0]
        size = context.args[1]
        season = context.args[2]
        quantity = int(context.args[3])


        context.user_data["new_tire"] = {
            "brand": brand,
            "size": size,
            "season": season,
            "quantity": quantity
        }


        await update.message.reply_text(
            "📸 Теперь отправьте фотографию этой шины."
        )


    except:

        await update.message.reply_text(
            "Пример:\n/add Michelin 205 зима 4"
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
        tire["season"],
        tire["quantity"],
        photo
    )


    del context.user_data["new_tire"]


    await update.message.reply_text(
        "✅ Шина добавлена вместе с фотографией!"
    )



async def remove(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_user.id != ADMIN_ID:

        await update.message.reply_text(
            "❌ У вас нет доступа."
        )
        return


    try:

        brand = context.args[0]
        size = context.args[1]
        season = context.args[2]
        quantity = int(context.args[3])


        if remove_tire(
            brand,
            size,
            season,
            quantity
        ):

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

        if update.message:
            await update.message.reply_text(
                "📦 Склад пока пуст."
            )
        else:
            await update.callback_query.message.reply_text(
                "📦 Склад пока пуст."
            )

        return



    total = 0
    brands = {}
    seasons = {}


    for tire in tires:

        quantity = tire["quantity"]

        total += quantity


        brand = tire["brand"]
        season = tire["season"]


        brands[brand] = brands.get(
            brand,
            0
        ) + quantity


        seasons[season] = seasons.get(
            season,
            0
        ) + quantity



    text = "📊 Отчёт склада\n\n"

    text += f"Всего шин: {total} шт.\n\n"


    text += "🏷 Бренды:\n"

    for brand, count in brands.items():

        text += f"{brand} — {count} шт.\n"



    text += "\n🌦 Сезон:\n"

    for season, count in seasons.items():

        text += f"{season} — {count} шт.\n"



    if update.message:

        await update.message.reply_text(text)

    else:

        await update.callback_query.message.reply_text(text)
