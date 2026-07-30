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
        InlineKeyboardButton("➕", callback_data=f"plus_{index}"),
        InlineKeyboardButton("➖", callback_data=f"minus_{index}")
    ]]

    markup = InlineKeyboardMarkup(keyboard)

    if tire.get("photo"):
        await query.edit_message_caption(
            caption=text,
            reply_markup=markup
        )
    else:
        await query.edit_message_text(
            text,
            reply_markup=markup
        )
