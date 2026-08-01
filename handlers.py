from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup
)

from telegram.ext import ContextTypes

from database import (
    add_tire,
    get_stock,
    remove_tire,
    find_tires,
    save_stock
)

from config import ADMIN_ID


# =========================
# СКЛАД
# =========================

async def stock(update: Update, context: ContextTypes.DEFAULT_TYPE):

    tires = get_stock()

    if not tires:
        await update.message.reply_text(
            "📦 Склад пока пуст."
        )
        return


    for i, tire in enumerate(tires):

        text = (
            f"📦 {tire['brand']}\n"
            f"📏 Размер: {tire['size']}\n"
            f"🛞 Тип: {tire.get('type','')}\n"
            f"📦 Количество: {tire.get('quantity',0)} шт.\n"
            f"💰 Цена: {tire.get('price',0)} руб."
        )


        keyboard = [[
            InlineKeyboardButton(
                "➕",
                callback_data=f"plus_{i}"
            ),
            InlineKeyboardButton(
                "➖",
                callback_data=f"minus_{i}"
            )
        ]]


        markup = InlineKeyboardMarkup(keyboard)


        if tire.get("photo"):

            await update.message.reply_photo(
                photo=tire["photo"],
                caption=text,
                reply_markup=markup
            )

        else:

            await update.message.reply_text(
                text,
                reply_markup=markup
            )



# =========================
# ДОБАВЛЕНИЕ
# =========================

async def add(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text(
            "❌ Нет доступа."
        )
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
            "📸 Теперь отправьте фото шины."
        )


    except:

        await update.message.reply_text(
            "Пример:\n"
            "/add Michelin 315/80R22.5 Рулевая 4 28000"
        )



# =========================
# СОХРАНЕНИЕ ФОТО
# =========================

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


    await update.message.reply_text(
        "✅ Шина добавлена на склад."
    )
# =========================
# УДАЛЕНИЕ
# =========================

async def remove(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text(
            "❌ Нет доступа."
        )
        return


    try:

        brand = context.args[0]
        size = context.args[1]
        tire_type = context.args[2]
        quantity = int(context.args[3])


        result = remove_tire(
            brand,
            size,
            tire_type,
            quantity
        )


        if result:
            await update.message.reply_text(
                "🗑 Шина удалена."
            )
        else:
            await update.message.reply_text(
                "❌ Такая шина не найдена."
            )


    except:

        await update.message.reply_text(
            "Пример:\n"
            "/remove Michelin 315/80R22.5 Рулевая 1"
        )



# =========================
# ПОИСК
# =========================

async def find(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not context.args:

        await update.message.reply_text(
            "Введите размер или марку."
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
            f"📏 {tire['size']}\n"
            f"🛞 {tire.get('type','')}\n"
            f"📦 {tire.get('quantity',0)} шт.\n"
            f"💰 {tire.get('price',0)} руб."
        )


        if tire.get("photo"):

            await update.message.reply_photo(
                photo=tire["photo"],
                caption=text
            )

        else:

            await update.message.reply_text(text)



# =========================
# ОТЧЁТ
# =========================

async def report(update: Update, context: ContextTypes.DEFAULT_TYPE):

    tires = get_stock()


    total = 0
    money = 0


    for tire in tires:

        total += tire.get("quantity",0)

        money += (
            tire.get("quantity",0)
            *
            tire.get("price",0)
        )


    text = (
        "📊 Отчёт склада\n\n"
        f"📦 Всего шин: {total} шт.\n"
        f"💰 Стоимость: {money} руб."
    )


    await update.message.reply_text(text)



# =========================
# ГЛАВНОЕ МЕНЮ
# =========================

async def menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = update.message.text


    if text == "📦 Склад":

        await stock(update, context)



    elif text == "🔍 Поиск":

        await update.message.reply_text(
            "Введите размер или марку."
        )



    elif text == "➕ Добавить":

        await update.message.reply_text(
            "Пример:\n"
            "/add Michelin 315/80R22.5 Рулевая 4 28000"
        )



    elif text == "🗑 Удалить":

        await update.message.reply_text(
            "Пример:\n"
            "/remove Michelin 315/80R22.5 Рулевая 1"
        )



    elif text == "📊 Отчёт":

        await report(update, context)



    elif text == "🔥 Быстрый поиск":

        keyboard = [

            ["295/80 R22.5"],
            ["315/70 R22.5"],
            ["315/80 R22.5"],
            ["385/65 R22.5"],
            ["11R22.5"],
            ["215/75 R17.5"],
            ["235/75 R17.5"]

        ]


        await update.message.reply_text(
            "Выберите размер:",
            reply_markup=ReplyKeyboardMarkup(
                keyboard,
                resize_keyboard=True
            )
        )



# =========================
# БЫСТРЫЙ ПОИСК
# =========================

async def quick_search_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = update.message.text


    sizes = [
        "295/80 R22.5",
        "315/70 R22.5",
        "315/80 R22.5",
        "385/65 R22.5",
        "11R22.5",
        "215/75 R17.5",
        "235/75 R17.5"
    ]


    if text in sizes:

        context.user_data["search_size"] = text


        keyboard = [

            ["🚛 Рулевая"],
            ["⚙️ Ведущая"],
            ["🛞 Прицепная"],
            ["⛏ Карьерная"],
            ["🌍 Универсальная"]

        ]


        await update.message.reply_text(
            "Выберите назначение:",
            reply_markup=ReplyKeyboardMarkup(
                keyboard,
                resize_keyboard=True
            )
        )

        return
# =========================
# ПРОДОЛЖЕНИЕ БЫСТРОГО ПОИСКА
# =========================

    types = [
        "🚛 Рулевая",
        "⚙️ Ведущая",
        "🛞 Прицепная",
        "⛏ Карьерная",
        "🌍 Универсальная"
    ]


    if text in types:

        tire_size = context.user_data.get("search_size")


        if not tire_size:
            await update.message.reply_text(
                "Сначала выберите размер."
            )
            return


        tires = get_stock()


        result = []


        for tire in tires:

            if (
                tire.get("size") == tire_size
                and tire.get("type") == text
            ):
                result.append(tire)



        if not result:

            await update.message.reply_text(
                "❌ Такой резины нет на складе."
            )
            return



        for tire in result:

            message = (
                f"🔍 Найдено:\n\n"
                f"📦 {tire['brand']}\n"
                f"📏 {tire['size']}\n"
                f"🛞 {tire.get('type','')}\n"
                f"📦 {tire.get('quantity',0)} шт.\n"
                f"💰 {tire.get('price',0)} руб."
            )


            if tire.get("photo"):

                await update.message.reply_photo(
                    photo=tire["photo"],
                    caption=message
                )

            else:

                await update.message.reply_text(message)



# =========================
# КНОПКИ + И -
# =========================

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    await query.answer()


    tires = get_stock()


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
        f"🛞 Тип: {tire.get('type','')}\n"
        f"📦 Количество: {tire.get('quantity',0)} шт.\n"
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
    if tire.get("photo"):
        await query.edit_message_caption(
            caption=text,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    else:
        await query.edit_message_text(
            text=text,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
