
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
)
from telegram.ext import ContextTypes

from database import (
    add_tire,
    get_stock,
    remove_tire,
    find_tires,
    save_stock,
)
from config import ADMIN_ID


SIZES = [
    "295/80r22.5",
    "315/70r22.5",
    "315/80r22.5",
    "385/65r22.5",
    "11r22.5",
    "215/75r17.5",
    "235/75r17.5",
]

TIRE_TYPES = {
    "🚛 рулевая": "рулевая",
    "⚙️ ведущая": "ведущая",
    "🛞 прицепная": "прицепная",
    "⛏ карьерная": "карьерная",
    "🌍 универсальная": "универсальная",
}


def normalize_size(text):
    text = str(text).lower().replace("ё", "е")
    return "".join(
        char for char in text
        if not char.isspace() and char not in "-–—"
    )


def clean_type(text):
    text = str(text).lower().strip().replace("ё", "е")

    for emoji in ("🚛", "⚙️", "🛞", "⛏", "🌍"):
        text = text.replace(emoji, "")

    return " ".join(text.split())


def tire_text(tire, title="📦"):
    return (
        f"{title} {tire.get('brand', '')}\n"
        f"📏 Размер: {tire.get('size', '')}\n"
        f"🛞 Тип: {tire.get('type', '')}\n"
        f"📦 Количество: {tire.get('quantity', 0)} шт.\n"
        f"💰 Цена: {tire.get('price', 0)} руб."
    )


def tire_keyboard(index):
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("➕", callback_data=f"plus_{index}"),
        InlineKeyboardButton("➖", callback_data=f"minus_{index}"),
    ]])


async def send_tire(update, tire, index=None, title="📦"):
    text = tire_text(tire, title)
    markup = tire_keyboard(index) if index is not None else None

    if tire.get("photo"):
        await update.message.reply_photo(
            photo=tire["photo"],
            caption=text,
            reply_markup=markup,
        )
    else:
        await update.message.reply_text(
            text,
            reply_markup=markup,
        )


async def stock(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tires = get_stock()

    if not tires:
        await update.message.reply_text("📦 Склад пока пуст.")
        return

    for index, tire in enumerate(tires):
        await send_tire(update, tire, index)


async def add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ Нет доступа.")
        return

    if len(context.args) < 5:
        await update.message.reply_text(
            "Пример:\n/add Michelin 315/80R22.5 Рулевая 4 28000"
        )
        return

    try:
        brand = context.args[0]
        size = context.args[1]
        tire_type = " ".join(context.args[2:-2])
        quantity = int(context.args[-2])
        price = int(context.args[-1])

        if quantity <= 0 or price < 0:
            raise ValueError

        context.user_data["new_tire"] = {
            "brand": brand,
            "size": size,
            "type": clean_type(tire_type),
            "quantity": quantity,
            "price": price,
        }

        await update.message.reply_text(
            "📸 Теперь отправьте фото шины."
        )

    except ValueError:
        await update.message.reply_text(
            "❌ Проверьте количество и цену.\n"
            "Пример:\n/add Michelin 315/80R22.5 Рулевая 4 28000"
        )


async def save_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    if "new_tire" not in context.user_data:
        return

    if not update.message.photo:
        await update.message.reply_text(
            "❌ Отправьте фотографию шины."
        )
        return

    photo = update.message.photo[-1].file_id
    tire = context.user_data["new_tire"]

    add_tire(
        tire["brand"],
        tire["size"],
        tire["type"],
        tire["quantity"],
        tire["price"],
        photo,
    )

    del context.user_data["new_tire"]
    await update.message.reply_text("✅ Шина добавлена на склад.")


async def remove(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ Нет доступа.")
        return

    if len(context.args) < 4:
        await update.message.reply_text(
            "Пример:\n/remove Michelin 315/80R22.5 Рулевая 1"
        )
        return

    try:
        brand = context.args[0]
        size = context.args[1]
        tire_type = " ".join(context.args[2:-1])
        quantity = int(context.args[-1])

        result = remove_tire(
            brand, size, clean_type(tire_type), quantity
        )

        await update.message.reply_text(
            "🗑 Количество обновлено."
            if result
            else "❌ Шина не найдена или количество указано неверно."
        )

    except ValueError:
        await update.message.reply_text(
            "❌ Количество должно быть числом."
        )


async def find(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text(
            "Введите марку, размер или назначение."
        )
        return

    tires = find_tires(" ".join(context.args))

    if not tires:
        await update.message.reply_text("❌ Ничего не найдено.")
        return

    for tire in tires:
        await send_tire(update, tire, title="🔍")


async def report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tires = get_stock()
    total = sum(t.get("quantity", 0) for t in tires)
    money = sum(
        t.get("quantity", 0) * t.get("price", 0)
        for t in tires
    )

    await update.message.reply_text(
        "📊 Отчёт склада\n\n"
        f"📦 Всего шин: {total} шт.\n"
        f"💰 Стоимость: {money} руб."
    )


async def menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()

    if text == "📦 Склад":
        await stock(update, context)
        return

    if text == "🔍 Поиск":
        context.user_data["waiting_search"] = True
        await update.message.reply_text(
            "Введите марку, размер или назначение."
        )
        return

    if text == "➕ Добавить":
        await update.message.reply_text(
            "Пример:\n/add Michelin 315/80R22.5 Рулевая 4 28000"
        )
        return

    if text == "🗑 Удалить":
        await update.message.reply_text(
            "Пример:\n/remove Michelin 315/80R22.5 Рулевая 1"
        )
        return

    if text == "📊 Отчёт":
        await report(update, context)
        return

    if text == "🔥 Быстрый поиск":
        keyboard = [
            ["295/80 R22.5"],
            ["315/70 R22.5"],
            ["315/80 R22.5"],
            ["385/65 R22.5"],
            ["11 R22.5"],
            ["215/75 R17.5"],
            ["235/75 R17.5"],
        ]

        await update.message.reply_text(
            "Выберите размер:",
            reply_markup=ReplyKeyboardMarkup(
                keyboard,
                resize_keyboard=True,
            ),
        )
        return

    normalized = normalize_size(text)

    if normalized in SIZES:
        context.user_data["search_size"] = normalized

        keyboard = [
            ["🚛 Рулевая"],
            ["⚙️ Ведущая"],
            ["🛞 Прицепная"],
            ["⛏ Карьерная"],
            ["🌍 Универсальная"],
        ]

        await update.message.reply_text(
            "Выберите назначение:",
            reply_markup=ReplyKeyboardMarkup(
                keyboard,
                resize_keyboard=True,
            ),
        )
        return

    tire_type = clean_type(text)

    if tire_type in TIRE_TYPES.values():
        size = context.user_data.get("search_size")

        if not size:
            await update.message.reply_text(
                "Сначала выберите размер через 🔥 Быстрый поиск."
            )
            return

        found = [
            tire for tire in get_stock()
            if normalize_size(tire.get("size", "")) == size
            and clean_type(tire.get("type", "")) == tire_type
        ]

        if not found:
            await update.message.reply_text(
                "❌ Такой резины нет на складе."
            )
            return

        for tire in found:
            await send_tire(update, tire, title="🔍")
        return

    if context.user_data.pop("waiting_search", False):
        tires = find_tires(text)

        if not tires:
            await update.message.reply_text("❌ Ничего не найдено.")
        else:
            for tire in tires:
                await send_tire(update, tire, title="🔍")


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    try:
        action, index_text = query.data.split("_", 1)
        index = int(index_text)
    except (ValueError, AttributeError):
        await query.message.reply_text(
            "❌ Не удалось обработать кнопку."
        )
        return

    tires = get_stock()

    if index < 0 or index >= len(tires):
        await query.message.reply_text(
            "❌ Запись не найдена. Откройте склад заново."
        )
        return

    tire = tires[index]

    if action == "plus":
        tire["quantity"] = tire.get("quantity", 0) + 1

    elif action == "minus":
        if tire.get("quantity", 0) > 1:
            tire["quantity"] -= 1
        else:
            await query.answer(
                "Количество не может быть меньше 1.",
                show_alert=True,
            )
            return
    else:
        return

    save_stock(tires)
    text = tire_text(tire)

    try:
        if query.message.photo:
            await query.edit_message_caption(
                caption=text,
                reply_markup=tire_keyboard(index),
            )
        else:
            await query.edit_message_text(
                text=text,
                reply_markup=tire_keyboard(index),
            )

    except Exception:
        await query.message.reply_text(
            f"✅ Количество сохранено: {tire['quantity']} шт."
        )
