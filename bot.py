from dotenv import load_dotenv
from os import getenv
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler
from telegram import Update
import logging

# loads .env content into env variables
load_dotenv()

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

BOT_TOKEN = getenv("BOT_TOKEN")


async def start_command_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Hello I'm Staff Question Beta Bot")

if __name__ == '__main__':
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    start_command = CommandHandler('start', start_command_handler)

    application.add_handler(start_command)

    application.run_polling()
