import os

from telegram import Update, ReplyKeyboardMarkup

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
    report,
    button_handler,
    menu_handler
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    keyboard = [
        ["📦 Склад", "🔍 Поиск"],
        ["➕ Добавить", "🗑 Удалить"],
        ["📊 Отчёт"],
        ["🔥 Быстрый поиск"]
    ]

    markup = ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True
    )

    await update.message.reply_text(
        "👋 Бот склада шин запущен!\n\nВыберите действие:",
        reply_markup=markup
    )


def main():

    token = os.getenv("TOKEN")

    if not token:
        print("❌ TOKEN не найден")
        return


    app = Application.builder().token(token).build()


    # Команды

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("stock", stock))
    app.add_handler(CommandHandler("add", add))
    app.add_handler(CommandHandler("remove", remove))
    app.add_handler(CommandHandler("find", find))
    app.add_handler(CommandHandler("report", report))


    # Сохранение фото

    app.add_handler(
        MessageHandler(
            filters.PHOTO,
            save_photo
        )
    )


    # Кнопки + -

    app.add_handler(
        CallbackQueryHandler(button_handler)
    )


    # Все кнопки меню и быстрый поиск
    # обрабатываются в одном месте

    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            menu_handler
        )
    )


    print("✅ Бот запущен")


    app.run_polling()


if __name__ == "__main__":
    main()
