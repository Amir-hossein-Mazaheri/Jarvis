from telegram.ext import ApplicationBuilder, CommandHandler, ConversationHandler, MessageHandler, filters, Defaults
from telegram.constants import ParseMode
from dotenv import load_dotenv
from os import getenv
import logging

from src.utils.db import connect_to_db
from src.constants.commands import START, REGISTER, CANCEL, EDIT, QUESTIONS, NEXT_QUESTION, SKIP_QUESTIONS, QUIT_QUESTIONS
from src.constants.other import RegisterMode
from src.constants.states import RegisterStates, EditStates, QuestionStates
from src.commands.register import start, ask_for_student_code, register_student_code, register_nickname, cancel_registration
from src.commands.edit import ask_to_edit_what, edit_decider, cancel_edit
from src.commands.questions import send_questions, cancel_questions, answer_validator, get_next_question, skip_question, quit_questions

# loads .env content into env variables
load_dotenv()

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

BOT_TOKEN = getenv("BOT_TOKEN")


def main():
    defaults = Defaults(parse_mode=ParseMode.HTML,
                        block=False, disable_notification=True)

    application = ApplicationBuilder().token(
        BOT_TOKEN).post_init(connect_to_db).defaults(defaults).build()

    start_handler = CommandHandler(START, start)

    register_handler = ConversationHandler(
        entry_points=[CommandHandler(REGISTER, ask_for_student_code)],
        states={
            RegisterStates.ASK_FOR_STUDENT_CODE: [CommandHandler(REGISTER, ask_for_student_code)],
            RegisterStates.REGISTER_STUDENT_CODE: [MessageHandler(filters.TEXT, register_student_code(RegisterMode.CREATE))],
            RegisterStates.REGISTER_NICKNAME: [MessageHandler(
                filters.TEXT, register_nickname(RegisterMode.CREATE))]
        },
        fallbacks=[CommandHandler(CANCEL, cancel_registration)]
    )

    edit_handler = ConversationHandler(
        entry_points=[CommandHandler(EDIT, ask_to_edit_what)],
        states={
            EditStates.ASK_TO_EDIT_WHAT: [CommandHandler(EDIT, ask_to_edit_what)],
            EditStates.EDIT_DECIDER: [MessageHandler(filters.TEXT, edit_decider)],
            EditStates.EDIT_STUDENT_CODE: [MessageHandler(
                filters.TEXT, register_student_code(RegisterMode.EDIT))],
            EditStates.EDIT_NICKNAME: [MessageHandler(
                filters.TEXT, register_nickname(RegisterMode.EDIT))]
        },
        fallbacks=[CommandHandler(CANCEL, cancel_edit)]
    )

    question_handler = ConversationHandler(
        entry_points=[CommandHandler(QUESTIONS, send_questions)],
        states={
            QuestionStates.SHOW_QUESTIONS: [CommandHandler(QUESTIONS, send_questions)],
            QuestionStates.ANSWER_VALIDATOR: [CommandHandler(SKIP_QUESTIONS, skip_question),
                                              CommandHandler(
                                                  QUIT_QUESTIONS, quit_questions),
                                              MessageHandler(filters.TEXT & (~filters.COMMAND), answer_validator)],
        },
        fallbacks=[CommandHandler(CANCEL, cancel_questions)]
    )

    application.add_handler(start_handler)
    application.add_handler(register_handler)
    application.add_handler(edit_handler)
    application.add_handler(question_handler)

    application.run_polling()


if __name__ == '__main__':
    main()
