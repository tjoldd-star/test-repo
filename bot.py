
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

TOKEN = os.environ.get("BOT_TOKEN")

PACKAGES = {
    "p1": ("100 алмазов", "10 сомони"),
    "p2": ("310 алмазов", "25 сомони"),
    "p3": ("520 алмазов", "40 сомони"),
    "p4": ("1060 алмазов", "80 сомони"),
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("💎 100 — 10 сомони", callback_data="p1")],
        [InlineKeyboardButton("💎 310 — 25 сомони", callback_data="p2")],
        [InlineKeyboardButton("💎 520 — 40 сомони", callback_data="p3")],
        [InlineKeyboardButton("💎 1060 — 80 сомони", callback_data="p4")],
    ]
    await update.message.reply_text(
        "🇹🇯 Добро пожаловать в FF AUTODONATE TJ!\n\n"
        "Выбери пакет алмазов:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def choose_package(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    name, price = PACKAGES[query.data]
    context.user_data["package"] = name
    await query.message.reply_text(
        f"Выбрано: {name}\nЦена: {price}\n\n"
        "Отправь свой игровой UID цифрами.\n"
        "Оплата и выдача алмазов пока не подключены."
    )
    context.user_data["waiting_uid"] = True

async def receive_uid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get("waiting_uid"):
        return
    uid = update.message.text.strip()
    if not uid.isdigit() or not 5 <= len(uid) <= 20:
        await update.message.reply_text("Проверь UID: нужны только цифры.")
        return
    context.user_data["waiting_uid"] = False
    await update.message.reply_text(
        f"Заказ подготовлен.\nПакет: {context.user_data['package']}\n"
        f"UID: {uid}\n\n"
        "Это тестовый заказ. Не оплачивай его: платёж ещё не подключён."
    )

def main():
    if not TOKEN:
        raise RuntimeError("Не задан BOT_TOKEN в переменных окружения")
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(choose_package, pattern=r"^p[1-4]$"))
    app.add_handler(CommandHandler("cancel", start))
    app.add_handler(__import__("telegram.ext", fromlist=["MessageHandler"]).MessageHandler(
        __import__("telegram.ext", fromlist=["filters"]).filters.TEXT
        & ~__import__("telegram.ext", fromlist=["filters"]).filters.COMMAND,
        receive_uid
    ))
    app.run_polling()

if __name__ == "__main__":
    main()
