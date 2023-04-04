from telegram.ext import CommandHandler, ConversationHandler, MessageHandler,\
    filters, CallbackQueryHandler, Application, JobQueue, ExtBot

from src.utils.db import connect_to_db
from src.utils.exact_matcher import exact_matcher
from src.utils.ensure_data_logs import ensure_data_logs
from src.constants.commands import START, REGISTER, BACK_TO_MENU, EDIT, QUESTIONS, SKIP_QUESTIONS,\
    QUIT_QUESTIONS, START_QUESTIONS, STAT, BACK_TO_STAT, QUESTIONS_HISTORY,\
    NEXT_QUESTIONS_PAGE, PREV_QUESTIONS_PAGE, ADMIN, REGISTER_ADMIN,\
    ADMIN_SHOW_USERS_LIST, BACK_TO_ADMIN_ACTIONS, ADMIN_PROMPT_ADD_QUESTION_BOX, SHOW_HELP, \
    ADMIN_SHOW_USERS_LIST_BUTTONS, TASK, BACK_TO_TASKS_ACTIONS, REMAINING_TASKS, DONE_TASKS, TOTAL_TASKS_SCORE, \
    TASK_INFORMATION_PREFIX, SUBMIT_TASK_PREFIX, SUBMIT_TASK, HEAD, HEAD_ADD_TASK, BACK_TO_HEAD_ACTIONS,\
    HEAD_SHOW_MARKED_TASKS, HEAD_APPROVE_TASK_PREFIX, HEAD_REMOVE_TASK_PREFIX, HEAD_SHOW_TASKS_TO_REMOVE, \
    REMOVE_QUESTION_BOX_PREFIX, HEAD_SHOW_QUESTIONS_BOX_TO_REMOVE, \
    ADMIN_SHOW_QUESTIONS_BOX_TO_REMOVE, HEAD_SHOW_QUESTION_BOXES_FOR_STAT, \
    GET_QUESTION_BOX_STAT_PREFIX, ADMIN_SHOW_QUESTION_BOXES_FOR_STAT, MENU, ADMIN_SHOW_HEADS_LIST_TO_REMOVE, \
    REMOVE_HEAD_PREFIX, ADD_HEAD_PREFIX, ADMIN_SHOW_NONE_HEAD_LIST_TO_REMOVE, REMOVE_USER_PREFIX,\
    QUESTION_BOX_PREP_PHASE_PREFIX, REGISTER_TEAM_PREFIX, EDIT_TEAM_PREFIX, ANSWER_VALIDATOR_PREFIX,\
    SHOW_QUESTION_BOX_STAT_PREFIX, HEAD_SEE_USERS_LIST, HEAD_ADD_USER_FROM_OTHER_TEAMS,\
    ADMIN_TOGGLE_EDIT_INFO, HEAD_REMOVE_USER_FROM_TEAM, HEAD_REMOVE_TEAM_MEMBER_PREFIX,\
    HEAD_ADD_MEMBER_FROM_OTHER_TEAMS_PREFIX, HEAD_SHOW_USERS_TO_MEMBER_ADD_FROM_OTHER_TEAM_PREFIX,\
    EDIT_INFO_PREFIX
from src.constants.other import RegisterMode
from src.constants.states import RegisterStates, EditStates, QuestionStates, StatStates,\
    AdminStates, TaskStates, HeadStates
from src.commands.register import start, ask_for_student_code, register_student_code,\
    register_nickname, register_team
from src.commands.edit import ask_to_edit_what, edit_decider
from src.commands.questions import send_questions, answer_validator,\
    skip_question, quit_questions, prep_phase, show_question_boxes
from src.commands.admin import show_admin_actions, register_admin, add_question_box, \
    show_users_list, add_head, show_users_list_buttons, show_heads_list_to_remove,\
    remove_head, remove_user, toggle_edit_info
from src.commands.other import questions_history, back_to_menu, show_help, cleaner, error_handler
from src.commands.stat import stat_decider, get_user_stat, show_question_box_stat
from src.commands.head import show_head_actions, prompt_add_task, add_task,\
    show_marked_tasks, approve_task, remove_task, show_tasks_to_remove,\
    show_questions_box_to_remove, remove_question_box, show_question_boxes_for_stat,\
    show_question_box_stat_and_percent, see_team_users_list, show_teams_to_add_team_member,\
    show_users_list_to_remove_from_team, add_team_member_from_other_teams, remove_team_member,\
    show_users_to_add_member_from_other_team
from src.commands.task import show_remaining_tasks, show_task_information, show_tasks_actions, show_done_tasks, show_tasks_total_score, mark_task


async def setup(
    application: Application[ExtBot, dict, dict, JobQueue],
):
    # make sure the app is connected to db before doing any action
    await connect_to_db()

    # make sure that data directory and data log files are created
    await ensure_data_logs()

    start_handler = CommandHandler(START, start)
    menu_handler = CommandHandler(MENU, back_to_menu)

    register_handler = ConversationHandler(
        per_chat=True,
        per_user=True,
        entry_points=[CallbackQueryHandler(
            ask_for_student_code, exact_matcher(REGISTER))],
        states={
            RegisterStates.REGISTER_STUDENT_CODE: [MessageHandler(filters.TEXT, register_student_code(RegisterMode.CREATE))],
            RegisterStates.REGISTER_TEAM: [CallbackQueryHandler(register_team(RegisterMode.CREATE), REGISTER_TEAM_PREFIX)],
            RegisterStates.REGISTER_NICKNAME: [MessageHandler(
                filters.TEXT, register_nickname(RegisterMode.CREATE))]
        },
        fallbacks=[CallbackQueryHandler(
            back_to_menu, exact_matcher(BACK_TO_MENU))]
    )

    edit_handler = ConversationHandler(
        per_chat=True,
        per_user=True,
        entry_points=[CallbackQueryHandler(
            ask_to_edit_what, exact_matcher(EDIT))],
        states={
            EditStates.EDIT_DECIDER: [CallbackQueryHandler(edit_decider, EDIT_INFO_PREFIX)],
            EditStates.EDIT_STUDENT_CODE: [MessageHandler(
                filters.TEXT, register_student_code(RegisterMode.EDIT))],
            EditStates.EDIT_NICKNAME: [MessageHandler(
                filters.TEXT, register_nickname(RegisterMode.EDIT))],
            EditStates.EDIT_TEAM: [CallbackQueryHandler(
                register_team(RegisterMode.EDIT), EDIT_TEAM_PREFIX)]
        },
        fallbacks=[CallbackQueryHandler(
            back_to_menu, exact_matcher(BACK_TO_MENU))]
    )

    question_handler = ConversationHandler(
        per_message=True,
        per_chat=True,
        per_user=True,
        entry_points=[CallbackQueryHandler(
            show_question_boxes, exact_matcher(QUESTIONS))],
        states={
            QuestionStates.PREP_PHASE: [
                CallbackQueryHandler(prep_phase, QUESTION_BOX_PREP_PHASE_PREFIX)],
            QuestionStates.SHOW_QUESTIONS: [
                CallbackQueryHandler(
                    send_questions, exact_matcher(START_QUESTIONS)),
                CallbackQueryHandler(show_question_boxes, exact_matcher(QUESTIONS))],
            QuestionStates.ANSWER_VALIDATOR: [
                CallbackQueryHandler(
                    skip_question, exact_matcher(SKIP_QUESTIONS)),
                CallbackQueryHandler(
                    quit_questions, exact_matcher(QUIT_QUESTIONS)),
                CallbackQueryHandler(answer_validator, ANSWER_VALIDATOR_PREFIX)],
        },
        fallbacks=[CallbackQueryHandler(
            back_to_menu, exact_matcher(BACK_TO_MENU))]
    )

    stat_handler = ConversationHandler(
        per_message=True,
        per_chat=True,
        per_user=True,
        entry_points=[CallbackQueryHandler(
            get_user_stat, exact_matcher(STAT))],
        states={
            StatStates.SELECT_QUESTION_BOX: [
                CallbackQueryHandler(show_question_box_stat, SHOW_QUESTION_BOX_STAT_PREFIX)],
            StatStates.DECIDER: [
                CallbackQueryHandler(
                    stat_decider, exact_matcher(BACK_TO_STAT))]
        },
        fallbacks=[CallbackQueryHandler(
            back_to_menu, exact_matcher(BACK_TO_MENU))]
    )

    admin_handler = ConversationHandler(
        per_chat=True,
        per_user=True,
        entry_points=[CallbackQueryHandler(
            show_admin_actions, exact_matcher(ADMIN)),
            CommandHandler(ADMIN, show_admin_actions)],
        states={
            AdminStates.SHOW_ADMIN_ACTIONS: [
                CallbackQueryHandler(show_admin_actions, exact_matcher(BACK_TO_ADMIN_ACTIONS))],
            AdminStates.REGISTER_USER_AS_AN_ADMIN: [
                CallbackQueryHandler(register_admin, exact_matcher(REGISTER_ADMIN))],
            AdminStates.ADMIN_ACTIONS: [
                CallbackQueryHandler(show_users_list_buttons(
                    ADD_HEAD_PREFIX, "هد"), exact_matcher(ADMIN_SHOW_USERS_LIST_BUTTONS)),
                CallbackQueryHandler(
                    show_users_list, exact_matcher(ADMIN_SHOW_USERS_LIST)),
                CallbackQueryHandler(show_questions_box_to_remove(
                    for_admin=True), exact_matcher(ADMIN_SHOW_QUESTIONS_BOX_TO_REMOVE)),
                CallbackQueryHandler(remove_question_box(
                    for_admin=True), REMOVE_QUESTION_BOX_PREFIX),
                CallbackQueryHandler(
                    show_admin_actions, exact_matcher(BACK_TO_ADMIN_ACTIONS)),
                MessageHandler(
                    filters.Document.Category(
                        'application/json'),
                    add_question_box(for_admin=True)),
                CallbackQueryHandler(
                    add_question_box(for_admin=True), exact_matcher(ADMIN_PROMPT_ADD_QUESTION_BOX)),
                CallbackQueryHandler(show_question_boxes_for_stat(
                    for_admin=True), exact_matcher(ADMIN_SHOW_QUESTION_BOXES_FOR_STAT)),
                CallbackQueryHandler(show_question_box_stat_and_percent(
                    for_admin=True), GET_QUESTION_BOX_STAT_PREFIX),
                CallbackQueryHandler(
                    show_heads_list_to_remove, exact_matcher(ADMIN_SHOW_HEADS_LIST_TO_REMOVE)),
                CallbackQueryHandler(
                    remove_head, REMOVE_HEAD_PREFIX),
                CallbackQueryHandler(
                    show_users_list_buttons(REMOVE_USER_PREFIX, "کاربر"), exact_matcher(ADMIN_SHOW_NONE_HEAD_LIST_TO_REMOVE)),
                CallbackQueryHandler(
                    remove_user, REMOVE_USER_PREFIX),
                CallbackQueryHandler(
                    add_head, ADD_HEAD_PREFIX),
                CallbackQueryHandler(
                    toggle_edit_info, exact_matcher(ADMIN_TOGGLE_EDIT_INFO))
            ],
        },
        fallbacks=[CallbackQueryHandler(
            back_to_menu, exact_matcher(BACK_TO_MENU))]
    )

    task_handler = ConversationHandler(
        per_chat=True,
        per_user=True,
        per_message=True,
        entry_points=[CallbackQueryHandler(
            show_tasks_actions, exact_matcher(TASK))],
        states={
            TaskStates.SHOW_TASKS_ACTIONS: [CallbackQueryHandler(show_tasks_actions, exact_matcher(BACK_TO_TASKS_ACTIONS))],
            TaskStates.TASK_ACTION_DECIDER: [
                CallbackQueryHandler(show_tasks_actions,
                                     exact_matcher(BACK_TO_TASKS_ACTIONS)),
                CallbackQueryHandler(
                    show_remaining_tasks(TASK_INFORMATION_PREFIX, "این تموم تسک هایی که برات گذاشتن", without_mark=False), exact_matcher(REMAINING_TASKS)),
                CallbackQueryHandler(
                    show_done_tasks, exact_matcher(DONE_TASKS)),
                CallbackQueryHandler(
                    show_tasks_total_score, exact_matcher(TOTAL_TASKS_SCORE)),
                CallbackQueryHandler(
                    show_task_information, TASK_INFORMATION_PREFIX),
                CallbackQueryHandler(
                    mark_task, SUBMIT_TASK_PREFIX),
                CallbackQueryHandler(show_remaining_tasks(
                    SUBMIT_TASK_PREFIX, "تسک هایی که میتونی ثبت کنی", without_mark=True), exact_matcher(SUBMIT_TASK)),
            ],
        },
        fallbacks=[CallbackQueryHandler(
            back_to_menu, exact_matcher(BACK_TO_MENU))]
    )

    head_handler = ConversationHandler(
        per_chat=True,
        per_user=True,
        entry_points=[CallbackQueryHandler(
            show_head_actions, exact_matcher(HEAD))],
        states={
            HeadStates.HEAD_ACTION_DECIDER: [
                CallbackQueryHandler(add_question_box(
                    for_admin=False), exact_matcher(ADMIN_PROMPT_ADD_QUESTION_BOX)),
                MessageHandler(filters.Document.Category(
                    "application/json"), add_question_box(for_admin=False)),
                CallbackQueryHandler(show_questions_box_to_remove(
                    for_admin=False), exact_matcher(HEAD_SHOW_QUESTIONS_BOX_TO_REMOVE)),
                CallbackQueryHandler(remove_question_box(
                    for_admin=False), REMOVE_QUESTION_BOX_PREFIX),
                CallbackQueryHandler(
                    prompt_add_task, exact_matcher(HEAD_ADD_TASK)),
                CallbackQueryHandler(
                    show_marked_tasks, exact_matcher(HEAD_SHOW_MARKED_TASKS)),
                CallbackQueryHandler(
                    approve_task, HEAD_APPROVE_TASK_PREFIX),
                CallbackQueryHandler(show_tasks_to_remove,
                                     exact_matcher(HEAD_SHOW_TASKS_TO_REMOVE)),
                CallbackQueryHandler(
                    remove_task, HEAD_REMOVE_TASK_PREFIX),
                CallbackQueryHandler(
                    show_question_boxes_for_stat(for_admin=False), exact_matcher(HEAD_SHOW_QUESTION_BOXES_FOR_STAT)),
                CallbackQueryHandler(
                    show_question_box_stat_and_percent(for_admin=False), GET_QUESTION_BOX_STAT_PREFIX),
                CallbackQueryHandler(see_team_users_list,
                                     exact_matcher(HEAD_SEE_USERS_LIST)),
                CallbackQueryHandler(show_users_list_to_remove_from_team, exact_matcher(
                    HEAD_REMOVE_USER_FROM_TEAM)),
                CallbackQueryHandler(remove_team_member,
                                     HEAD_REMOVE_TEAM_MEMBER_PREFIX),
                CallbackQueryHandler(show_teams_to_add_team_member, exact_matcher(
                    HEAD_ADD_USER_FROM_OTHER_TEAMS)),
                CallbackQueryHandler(
                    add_team_member_from_other_teams, HEAD_ADD_MEMBER_FROM_OTHER_TEAMS_PREFIX),
                CallbackQueryHandler(show_users_to_add_member_from_other_team,
                                     HEAD_SHOW_USERS_TO_MEMBER_ADD_FROM_OTHER_TEAM_PREFIX)
            ],
            HeadStates.HEAD_ADD_TASK: [MessageHandler(
                filters.Document.Category("application/json"), add_task)]
        },
        fallbacks=[
            CallbackQueryHandler(
                show_head_actions, exact_matcher(BACK_TO_HEAD_ACTIONS)),
            CallbackQueryHandler(back_to_menu, exact_matcher(BACK_TO_MENU))
        ]
    )

    history_handlers = [
        CallbackQueryHandler(
            questions_history, exact_matcher(QUESTIONS_HISTORY)),
        CallbackQueryHandler(
            questions_history, exact_matcher(NEXT_QUESTIONS_PAGE)),
        CallbackQueryHandler(
            questions_history, exact_matcher(PREV_QUESTIONS_PAGE))
    ]

    back_to_menu_handler = CallbackQueryHandler(
        back_to_menu, exact_matcher(BACK_TO_MENU))
    show_help_handler = CallbackQueryHandler(
        show_help, exact_matcher(SHOW_HELP))

    application.add_handler(start_handler)
    application.add_handler(menu_handler)
    application.add_handler(task_handler)
    application.add_handler(head_handler)
    application.add_handler(admin_handler)
    application.add_handler(register_handler)
    application.add_handler(edit_handler)
    application.add_handler(question_handler)
    application.add_handler(stat_handler)
    application.add_handler(back_to_menu_handler)
    application.add_handler(show_help_handler)
    application.add_handler(MessageHandler(
        filters.ALL & (~filters.COMMAND), cleaner))

    application.add_handlers(history_handlers)

    application.add_error_handler(error_handler)

    commands = [
        ("start", "استارت ربات و نمایش منوی ربات")
    ]

    await application.bot.set_my_commands(commands)
