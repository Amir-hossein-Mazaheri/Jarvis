from telegram.ext import ConversationHandler, MessageHandler,\
    filters, Application, JobQueue, ExtBot

from src.utils.db import connect_to_db
from src.utils.SuperCallbackQueryHandler import SuperCallbackQueryHandler
from src.utils.SuperCommandHandler import SuperCommandHandler
from src.utils.SuperMessageHandler import SuperMessageHandler
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
    EDIT_INFO_PREFIX, ADMIN_PUBLIC_ANNOUNCEMENT, ADMIN_PUBLIC_VERSION_CHANGE_ANNOUNCEMENT,\
    ADMIN_NEXT_USERS_PAGE_PREFIX, ADMIN_PREV_USERS_PAGE_PREFIX
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
    remove_head, remove_user, toggle_edit_info, public_announcement, public_announcement_about_version_change
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

    start_handler = SuperCommandHandler(START, start, guard="none")
    menu_handler = SuperCommandHandler(MENU, back_to_menu, guard="none")

    register_handler = ConversationHandler(
        per_chat=True,
        per_user=True,
        entry_points=[
            SuperCallbackQueryHandler(
                ask_for_student_code, REGISTER, guard="none")
        ],
        states={
            RegisterStates.REGISTER_STUDENT_CODE: [
                SuperMessageHandler(
                    filters.TEXT, register_student_code(RegisterMode.CREATE), "none")
            ],
            RegisterStates.REGISTER_TEAM: [
                SuperCallbackQueryHandler(register_team(
                    RegisterMode.CREATE), REGISTER_TEAM_PREFIX, "prefix", "none")
            ],
            RegisterStates.REGISTER_NICKNAME: [
                SuperMessageHandler(
                    filters.TEXT, register_nickname(RegisterMode.CREATE), "none")
            ]
        },
        fallbacks=[SuperCallbackQueryHandler(
            back_to_menu, BACK_TO_MENU, guard="none")]
    )

    edit_handler = ConversationHandler(
        per_chat=True,
        per_user=True,
        entry_points=[
            SuperCallbackQueryHandler(ask_to_edit_what, EDIT)
        ],
        states={
            EditStates.EDIT_DECIDER: [
                SuperCallbackQueryHandler(
                    edit_decider, EDIT_INFO_PREFIX, "prefix")
            ],
            EditStates.EDIT_STUDENT_CODE: [
                SuperMessageHandler(
                    filters.TEXT, register_student_code(RegisterMode.EDIT))
            ],
            EditStates.EDIT_NICKNAME: [
                SuperMessageHandler(
                    filters.TEXT, register_nickname(RegisterMode.EDIT))
            ],
            EditStates.EDIT_TEAM: [
                SuperCallbackQueryHandler(
                    register_team(RegisterMode.EDIT), EDIT_TEAM_PREFIX, "prefix")
            ]
        },
        fallbacks=[SuperCallbackQueryHandler(
            back_to_menu, BACK_TO_MENU, guard="none")]
    )

    question_handler = ConversationHandler(
        per_message=True,
        per_chat=True,
        per_user=True,
        entry_points=[
            SuperCallbackQueryHandler(show_question_boxes, QUESTIONS)
        ],
        states={
            QuestionStates.PREP_PHASE: [
                SuperCallbackQueryHandler(
                    prep_phase, QUESTION_BOX_PREP_PHASE_PREFIX, "prefix")
            ],
            QuestionStates.SHOW_QUESTIONS: [
                SuperCallbackQueryHandler(send_questions, START_QUESTIONS),
                SuperCallbackQueryHandler(show_question_boxes, QUESTIONS)
            ],
            QuestionStates.ANSWER_VALIDATOR: [
                SuperCallbackQueryHandler(skip_question, SKIP_QUESTIONS),
                SuperCallbackQueryHandler(quit_questions, QUIT_QUESTIONS),
                SuperCallbackQueryHandler(
                    answer_validator, ANSWER_VALIDATOR_PREFIX, "prefix")
            ],
        },
        fallbacks=[SuperCallbackQueryHandler(
            back_to_menu, BACK_TO_MENU, guard="none")]
    )

    stat_handler = ConversationHandler(
        per_message=True,
        per_chat=True,
        per_user=True,
        entry_points=[
            SuperCallbackQueryHandler(get_user_stat, STAT)
        ],
        states={
            StatStates.SELECT_QUESTION_BOX: [
                SuperCallbackQueryHandler(
                    show_question_box_stat, SHOW_QUESTION_BOX_STAT_PREFIX, "prefix")
            ],
            StatStates.DECIDER: [
                SuperCallbackQueryHandler(
                    stat_decider, exact_matcher(BACK_TO_STAT), "prefix")
            ]
        },
        fallbacks=[SuperCallbackQueryHandler(
            back_to_menu, BACK_TO_MENU, guard="none")]
    )

    admin_handler = ConversationHandler(
        per_chat=True,
        per_user=True,
        entry_points=[
            SuperCallbackQueryHandler(
                show_admin_actions, ADMIN, guard="none"),
            SuperCommandHandler(ADMIN, show_admin_actions)],
        states={
            AdminStates.SHOW_ADMIN_ACTIONS: [
                SuperCallbackQueryHandler(
                    show_admin_actions, BACK_TO_ADMIN_ACTIONS, guard="none")
            ],
            AdminStates.REGISTER_USER_AS_AN_ADMIN: [
                SuperCallbackQueryHandler(
                    register_admin, REGISTER_ADMIN, guard="none")
            ],
            AdminStates.ADMIN_ACTIONS: [
                SuperCallbackQueryHandler(show_users_list_buttons(
                    ADD_HEAD_PREFIX, "هد"), ADMIN_SHOW_USERS_LIST_BUTTONS, guard="admin"),

                SuperCallbackQueryHandler(
                    show_users_list, ADMIN_SHOW_USERS_LIST, guard="admin"),

                SuperCallbackQueryHandler(
                    show_users_list, ADMIN_NEXT_USERS_PAGE_PREFIX, "prefix", "admin"),

                SuperCallbackQueryHandler(
                    show_users_list, ADMIN_PREV_USERS_PAGE_PREFIX, "prefix", "admin"),

                SuperCallbackQueryHandler(show_questions_box_to_remove(
                    for_admin=True), ADMIN_SHOW_QUESTIONS_BOX_TO_REMOVE, guard="admin"),

                SuperCallbackQueryHandler(remove_question_box(
                    for_admin=True), REMOVE_QUESTION_BOX_PREFIX, "prefix", "admin"),

                SuperCallbackQueryHandler(
                    show_admin_actions, BACK_TO_ADMIN_ACTIONS, guard="none"),

                SuperMessageHandler(
                    filters.Document.Category(
                        'application/json'),
                    add_question_box(for_admin=True), "admin"),

                SuperCallbackQueryHandler(
                    add_question_box(for_admin=True), ADMIN_PROMPT_ADD_QUESTION_BOX, guard="none"),

                SuperCallbackQueryHandler(show_question_boxes_for_stat(
                    for_admin=True), ADMIN_SHOW_QUESTION_BOXES_FOR_STAT, guard="admin"),

                SuperCallbackQueryHandler(show_question_box_stat_and_percent(
                    for_admin=True), GET_QUESTION_BOX_STAT_PREFIX, "prefix", "admin"),

                SuperCallbackQueryHandler(
                    show_heads_list_to_remove, ADMIN_SHOW_HEADS_LIST_TO_REMOVE, guard="admin"),

                SuperCallbackQueryHandler(
                    remove_head, REMOVE_HEAD_PREFIX, "prefix", "admin"),

                SuperCallbackQueryHandler(
                    show_users_list_buttons(REMOVE_USER_PREFIX, "کاربر"), ADMIN_SHOW_NONE_HEAD_LIST_TO_REMOVE, guard="admin"),

                SuperCallbackQueryHandler(
                    remove_user, REMOVE_USER_PREFIX, "prefix", "admin"),

                SuperCallbackQueryHandler(
                    add_head, ADD_HEAD_PREFIX, "prefix", "admin"),

                SuperCallbackQueryHandler(
                    toggle_edit_info, ADMIN_TOGGLE_EDIT_INFO, guard="admin"),

                SuperCallbackQueryHandler(
                    public_announcement, ADMIN_PUBLIC_ANNOUNCEMENT, guard="admin"
                ),

                SuperCallbackQueryHandler(
                    public_announcement_about_version_change, ADMIN_PUBLIC_VERSION_CHANGE_ANNOUNCEMENT, guard="admin"
                ),
            ],
            AdminStates.PUBLIC_ANNOUNCEMENT: [
                SuperMessageHandler(
                    filters.TEXT, public_announcement, guard="admin"
                )
            ],
            AdminStates.PUBLIC_VERSION_CHANGE_ANNOUNCEMENT: [
                SuperMessageHandler(
                    filters.TEXT, public_announcement_about_version_change, guard="admin")
            ]
        },
        fallbacks=[SuperCallbackQueryHandler(
            back_to_menu, BACK_TO_MENU, guard="none")]
    )

    task_handler = ConversationHandler(
        per_chat=True,
        per_user=True,
        per_message=True,
        entry_points=[
            SuperCallbackQueryHandler(show_tasks_actions, TASK)
        ],
        states={
            TaskStates.SHOW_TASKS_ACTIONS: [
                SuperCallbackQueryHandler(
                    show_tasks_actions, BACK_TO_TASKS_ACTIONS)
            ],
            TaskStates.TASK_ACTION_DECIDER: [
                SuperCallbackQueryHandler(show_tasks_actions,
                                          BACK_TO_TASKS_ACTIONS),
                SuperCallbackQueryHandler(
                    show_remaining_tasks(
                        TASK_INFORMATION_PREFIX, "این تموم تسک هایی که برات گذاشتن", without_mark=False),
                    REMAINING_TASKS),
                SuperCallbackQueryHandler(
                    show_done_tasks, DONE_TASKS),
                SuperCallbackQueryHandler(
                    show_tasks_total_score, TOTAL_TASKS_SCORE),
                SuperCallbackQueryHandler(
                    show_task_information, TASK_INFORMATION_PREFIX, "prefix"),
                SuperCallbackQueryHandler(
                    mark_task, SUBMIT_TASK_PREFIX, "prefix"),
                SuperCallbackQueryHandler(show_remaining_tasks(
                    SUBMIT_TASK_PREFIX, "تسک هایی که میتونی ثبت کنی", without_mark=True), SUBMIT_TASK),
            ],
        },
        fallbacks=[SuperCallbackQueryHandler(back_to_menu, BACK_TO_MENU)]
    )

    head_handler = ConversationHandler(
        per_chat=True,
        per_user=True,
        entry_points=[SuperCallbackQueryHandler(
            show_head_actions, HEAD, guard="head")],
        states={
            HeadStates.HEAD_ACTION_DECIDER: [
                SuperCallbackQueryHandler(add_question_box(
                    for_admin=False), ADMIN_PROMPT_ADD_QUESTION_BOX, guard="head"),
                SuperMessageHandler(filters.Document.Category(
                    "application/json"), add_question_box(for_admin=False), "head"),
                SuperCallbackQueryHandler(show_questions_box_to_remove(
                    for_admin=False), HEAD_SHOW_QUESTIONS_BOX_TO_REMOVE, guard="head"),
                SuperCallbackQueryHandler(remove_question_box(
                    for_admin=False), REMOVE_QUESTION_BOX_PREFIX, "prefix", "head"),
                SuperCallbackQueryHandler(
                    prompt_add_task, HEAD_ADD_TASK, guard="head"),
                SuperCallbackQueryHandler(
                    show_marked_tasks, HEAD_SHOW_MARKED_TASKS, guard="head"),
                SuperCallbackQueryHandler(
                    approve_task, HEAD_APPROVE_TASK_PREFIX, "prefix", "head"),
                SuperCallbackQueryHandler(show_tasks_to_remove,
                                          HEAD_SHOW_TASKS_TO_REMOVE, guard="head"),
                SuperCallbackQueryHandler(
                    remove_task, HEAD_REMOVE_TASK_PREFIX, "prefix", "head"),
                SuperCallbackQueryHandler(
                    show_question_boxes_for_stat(for_admin=False), HEAD_SHOW_QUESTION_BOXES_FOR_STAT, guard="head"),
                SuperCallbackQueryHandler(
                    show_question_box_stat_and_percent(for_admin=False), GET_QUESTION_BOX_STAT_PREFIX, "prefix", "head"),
                SuperCallbackQueryHandler(see_team_users_list,
                                          HEAD_SEE_USERS_LIST, guard="head"),
                SuperCallbackQueryHandler(show_users_list_to_remove_from_team,
                                          HEAD_REMOVE_USER_FROM_TEAM, guard="head"),
                SuperCallbackQueryHandler(remove_team_member,
                                          HEAD_REMOVE_TEAM_MEMBER_PREFIX, "prefix", "head"),
                SuperCallbackQueryHandler(show_teams_to_add_team_member,
                                          HEAD_ADD_USER_FROM_OTHER_TEAMS, guard="head"),
                SuperCallbackQueryHandler(
                    add_team_member_from_other_teams, HEAD_ADD_MEMBER_FROM_OTHER_TEAMS_PREFIX, "prefix", "head"),
                SuperCallbackQueryHandler(show_users_to_add_member_from_other_team,
                                          HEAD_SHOW_USERS_TO_MEMBER_ADD_FROM_OTHER_TEAM_PREFIX, "prefix", "head")
            ],
            HeadStates.HEAD_ADD_TASK: [SuperMessageHandler(
                filters.Document.Category("application/json"), add_task, "head")]
        },
        fallbacks=[
            SuperCallbackQueryHandler(
                show_head_actions, BACK_TO_HEAD_ACTIONS, guard="head"),
            SuperCallbackQueryHandler(back_to_menu, BACK_TO_MENU)
        ]
    )

    history_handlers = [
        SuperCallbackQueryHandler(questions_history, QUESTIONS_HISTORY),
        SuperCallbackQueryHandler(questions_history, NEXT_QUESTIONS_PAGE),
        SuperCallbackQueryHandler(questions_history, PREV_QUESTIONS_PAGE)
    ]

    back_to_menu_handler = SuperCallbackQueryHandler(
        back_to_menu, BACK_TO_MENU, guard="none")
    show_help_handler = SuperCallbackQueryHandler(
        show_help, SHOW_HELP, guard="none")

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
