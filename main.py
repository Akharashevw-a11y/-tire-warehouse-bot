import os
from telegram.ext import Application, CommandHandler
from handlers import stock, add, remove


TOKEN = os.getenv("TOKEN")


async def start(update, context):
    await update.message.reply_text(
        "Привет! 👋\n\n"
        "Доступные команды:\n"
        "/stock — показать склад\n"
        "/add — добавить шины\n"
        "/remove — удалить шины"
    )


def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("stock", stock))
    app.add_handler(CommandHandler("add", add))
    app.add_handler(CommandHandler("remove", remove))

    app.run_polling()


if __name__ == "__main__":
    main()
