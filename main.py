from telegram.ext import ApplicationBuilder, CommandHandler, ConversationHandler, MessageHandler,\
    filters, Defaults, CallbackQueryHandler
from telegram.constants import ParseMode
from dotenv import load_dotenv
import os
import logging

from src.utils.db import connect_to_db
from src.constants.commands import START, REGISTER, CANCEL, EDIT, QUESTIONS, SKIP_QUESTIONS,\
    QUIT_QUESTIONS, START_QUESTIONS, CANCEL_QUESTIONS, STAT, BACK_TO_STAT, QUESTIONS_HISTORY,\
    NEXT_QUESTIONS_PAGE, PREV_QUESTIONS_PAGE, ADMIN, REGISTER_ADMIN,\
    ADMIN_SHOW_USERS_LIST, BACK_TO_ADMIN_ACTIONS, ADMIN_PROMPT_ADD_QUESTION_BOX
from src.constants.other import RegisterMode
from src.constants.states import RegisterStates, EditStates, QuestionStates, StatStates, AdminStates
from src.commands.register import start, ask_for_student_code, register_student_code,\
    register_nickname, cancel_registration
from src.commands.edit import ask_to_edit_what, edit_decider, cancel_edit
from src.commands.questions import send_questions, cancel_questions, answer_validator,\
    skip_question, quit_questions, prep_phase
from src.commands.admin import show_admin_actions, register_admin, add_question_box, show_users_list, cancel_admin
from src.commands.other import get_user_stat, cancel_stat, show_question_box_stat, stat_decider,\
    questions_history

# loads .env content into env variables
load_dotenv()

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

BOT_TOKEN = os.getenv("BOT_TOKEN")


def main():
    defaults = Defaults(parse_mode=ParseMode.HTML,
                        block=False, disable_notification=True)

    application = ApplicationBuilder().token(
        BOT_TOKEN).post_init(connect_to_db).defaults(defaults).build()

    start_handler = CommandHandler(START, start)

    register_handler = ConversationHandler(
        entry_points=[CommandHandler(REGISTER, ask_for_student_code), CallbackQueryHandler(
            ask_for_student_code, REGISTER)],
        states={
            RegisterStates.ASK_FOR_STUDENT_CODE: [CommandHandler(REGISTER, ask_for_student_code)],
            RegisterStates.REGISTER_STUDENT_CODE: [CallbackQueryHandler(cancel_registration, CANCEL), MessageHandler(filters.TEXT, register_student_code(RegisterMode.CREATE))],
            RegisterStates.REGISTER_NICKNAME: [CallbackQueryHandler(cancel_registration, CANCEL),
                                               MessageHandler(
                filters.TEXT, register_nickname(RegisterMode.CREATE))]
        },
        fallbacks=[CommandHandler(CANCEL, cancel_registration)]
    )

    edit_handler = ConversationHandler(
        entry_points=[CommandHandler(
            EDIT, ask_to_edit_what), CallbackQueryHandler(ask_to_edit_what, EDIT)],
        states={
            EditStates.ASK_TO_EDIT_WHAT: [CommandHandler(EDIT, ask_to_edit_what)],
            EditStates.EDIT_DECIDER: [CallbackQueryHandler(cancel_edit, CANCEL), CallbackQueryHandler(edit_decider)],
            EditStates.EDIT_STUDENT_CODE: [MessageHandler(
                filters.TEXT, register_student_code(RegisterMode.EDIT))],
            EditStates.EDIT_NICKNAME: [MessageHandler(
                filters.TEXT, register_nickname(RegisterMode.EDIT))]
        },
        fallbacks=[CommandHandler(CANCEL, cancel_edit)]
    )

    question_handler = ConversationHandler(
        entry_points=[CommandHandler(
            QUESTIONS, prep_phase), CallbackQueryHandler(prep_phase, QUESTIONS)],
        states={
            QuestionStates.SHOW_QUESTIONS: [CallbackQueryHandler(send_questions, START_QUESTIONS), CallbackQueryHandler(cancel_questions, CANCEL_QUESTIONS)],
            QuestionStates.ANSWER_VALIDATOR: [CallbackQueryHandler(skip_question, SKIP_QUESTIONS),
                                              CallbackQueryHandler(
                                                  quit_questions, QUIT_QUESTIONS),
                                              CallbackQueryHandler(answer_validator)],
        },
        fallbacks=[CommandHandler(CANCEL, cancel_questions)]
    )

    stat_handler = ConversationHandler(
        entry_points=[CommandHandler(
            STAT, get_user_stat), CallbackQueryHandler(get_user_stat, STAT)],
        states={
            StatStates.SHOW_STAT: [CallbackQueryHandler(get_user_stat)],
            StatStates.SELECT_QUESTION_BOX: [
                CallbackQueryHandler(show_question_box_stat)],
            StatStates.DECIDER: [CallbackQueryHandler(
                stat_decider, BACK_TO_STAT)]
        },
        fallbacks=[CommandHandler(CANCEL, cancel_stat)]
    )

    admin_handler = ConversationHandler(
        entry_points=[CommandHandler(ADMIN, show_admin_actions)],
        states={
            AdminStates.SHOW_ADMIN_ACTIONS: [CallbackQueryHandler(show_admin_actions, BACK_TO_ADMIN_ACTIONS)],
            AdminStates.REGISTER_ADMIN: [
                CallbackQueryHandler(register_admin, REGISTER_ADMIN)],
            AdminStates.ADMIN_ACTIONS: [CallbackQueryHandler(show_users_list, ADMIN_SHOW_USERS_LIST),
                                        CallbackQueryHandler(
                                            show_admin_actions, BACK_TO_ADMIN_ACTIONS),
                                        MessageHandler(
                                            filters.Document.Category(
                                                'application/json'),
                                            add_question_box),
                                        CallbackQueryHandler(
                                            cancel_admin, CANCEL),
                                        CallbackQueryHandler(add_question_box, ADMIN_PROMPT_ADD_QUESTION_BOX)],
        },
        fallbacks=[]
    )

    history_handlers = [
        CommandHandler(QUESTIONS_HISTORY, questions_history),
        CallbackQueryHandler(questions_history, QUESTIONS_HISTORY),
        CallbackQueryHandler(questions_history, NEXT_QUESTIONS_PAGE),
        CallbackQueryHandler(questions_history, PREV_QUESTIONS_PAGE)
    ]

    application.add_handler(start_handler)
    application.add_handler(register_handler)
    application.add_handler(edit_handler)
    application.add_handler(question_handler)
    application.add_handler(stat_handler)
    application.add_handler(admin_handler)

    application.add_handlers(history_handlers)

    application.run_polling()


if __name__ == '__main__':
    main()
