import os
import logging
from telegram.ext import ApplicationBuilder, Defaults
from telegram.constants import ParseMode
from dotenv import load_dotenv

from src.utils.setup import setup

# loads .env content into env variables
load_dotenv()

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

BOT_TOKEN = os.getenv("BOT_TOKEN")
program_mode = os.getenv("MODE")


def main():
    defaults = Defaults(parse_mode=ParseMode.HTML)

    application = ApplicationBuilder().token(
        BOT_TOKEN).post_init(setup).defaults(defaults).build()

    if program_mode.lower() == 'production':
        application.run_webhook(
            listen="0.0.0.0",
            port=8443,
            secret_token=os.getenv("BOT_SECRET"),
            key="private.key",
            cert="cert.pem",
            webhook_url=os.getenv("SERVER_IP")
        )
    else:
        application.run_polling()


if __name__ == '__main__':
    main()
