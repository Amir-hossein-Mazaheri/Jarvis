from dotenv import load_dotenv
from os import getenv
import logging

from telegram.ext import ApplicationBuilder, CommandHandler, ConversationHandler, MessageHandler, filters
from src.constants.commands import START, REGISTER, CANCEL, EDIT
from src.constants.other import RegisterMode
from src.commands.register import start, ask_for_student_code, register_student_code, register_nickname, cancel_registration, ASK_FOR_STUDENT_CODE, REGISTER_NICKNAME, REGISTER_STUDENT_CODE
from src.commands.edit import ask_to_edit_what, edit_decider, cancel_edit,  ASK_TO_EDIT_WHAT, EDIT_DECIDER, EDIT_NICKNAME, EDIT_STUDENT_CODE

# loads .env content into env variables
load_dotenv()

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

BOT_TOKEN = getenv("BOT_TOKEN")


def main():
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    start_handler = CommandHandler(START, start)
    register_handler = ConversationHandler(
        entry_points=[CommandHandler(REGISTER, ask_for_student_code)],
        states={
            ASK_FOR_STUDENT_CODE: [CommandHandler(REGISTER, ask_for_student_code)],
            REGISTER_STUDENT_CODE: [MessageHandler(filters.TEXT, register_student_code(RegisterMode.CREATE))],
            REGISTER_NICKNAME: [MessageHandler(
                filters.TEXT, register_nickname(RegisterMode.CREATE))]
        },
        fallbacks=[CommandHandler(CANCEL, cancel_registration)]
    )

    edit_handler = ConversationHandler(
        entry_points=[CommandHandler(EDIT, ask_to_edit_what)],
        states={
            ASK_TO_EDIT_WHAT: [CommandHandler(EDIT, ask_to_edit_what)],
            EDIT_DECIDER: [MessageHandler(filters.TEXT, edit_decider)],
            EDIT_STUDENT_CODE: [MessageHandler(
                filters.TEXT, register_student_code(RegisterMode.EDIT))],
            EDIT_NICKNAME: [MessageHandler(
                filters.TEXT, register_nickname(RegisterMode.EDIT))]
        },
        fallbacks=[CommandHandler(CANCEL, cancel_edit)]
    )

    application.add_handler(start_handler)
    application.add_handler(register_handler)
    application.add_handler(edit_handler)

    application.run_polling()


if __name__ == '__main__':
    main()
