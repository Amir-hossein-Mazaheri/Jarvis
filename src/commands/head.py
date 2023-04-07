from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from prisma.enums import Team, UserRole
from datetime import datetime, timedelta
import json

from src.utils.db import db
from src.utils.get_back_to_menu_button import get_back_to_menu_button
from src.utils.task_validator import task_validator
from src.utils.send_question_boxes import send_question_boxes
from src.utils.get_head_common_keyboard import get_head_common_keyboard
from src.utils.send_notification import send_notification
from src.utils.get_user import get_user
from src.utils.show_user import show_user
from src.utils.get_teams_keyboard import get_teams_keyboard
from src.utils.add_task_handler import add_task_handler
from src.constants.states import HeadStates, AdminStates
from src.constants.commands import ADMIN_PROMPT_ADD_QUESTION_BOX, HEAD_ADD_TASK,\
    HEAD_APPROVE_TASK_PREFIX, HEAD_SHOW_MARKED_TASKS, HEAD_SHOW_TASKS_TO_REMOVE,\
    HEAD_REMOVE_TASK_PREFIX, REMOVE_QUESTION_BOX_PREFIX, HEAD_SHOW_QUESTIONS_BOX_TO_REMOVE, \
    GET_QUESTION_BOX_STAT_PREFIX, HEAD_SHOW_QUESTION_BOXES_FOR_STAT, HEAD_SEE_USERS_LIST,\
    HEAD_ADD_USER_FROM_OTHER_TEAMS, HEAD_REMOVE_USER_FROM_TEAM, HEAD_ADD_MEMBER_FROM_OTHER_TEAMS_PREFIX,\
    HEAD_REMOVE_TEAM_MEMBER_PREFIX, HEAD_SHOW_USERS_TO_MEMBER_ADD_FROM_OTHER_TEAM_PREFIX


async def show_head_actions(update: Update, ctx: ContextTypes.DEFAULT_TYPE, message_sender):
    questions_box_buttons = [InlineKeyboardButton(
        "❓ " + "افزودن آزمون", callback_data=ADMIN_PROMPT_ADD_QUESTION_BOX),
        InlineKeyboardButton("💯 " + "وضعیت آزمون ها",
                             callback_data=HEAD_SHOW_QUESTION_BOXES_FOR_STAT),
        InlineKeyboardButton("❌❓ " + "حذف آزمون",
                             callback_data=HEAD_SHOW_QUESTIONS_BOX_TO_REMOVE),
    ]

    questions_box_buttons.reverse()

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🧑‍🤝‍🧑 " + "اعضای تیمت",
                              callback_data=HEAD_SEE_USERS_LIST)],
        [InlineKeyboardButton("❌ " + "حذف تسک", callback_data=HEAD_SHOW_TASKS_TO_REMOVE),
         InlineKeyboardButton("⚒️ " + "افزودن تسک", callback_data=HEAD_ADD_TASK),],
        questions_box_buttons,
        [InlineKeyboardButton("✅ " + "تایید تسک های تیمت",
                              callback_data=HEAD_SHOW_MARKED_TASKS)],
        [InlineKeyboardButton("❌👤 " + "حذف عضو از تیم", callback_data=HEAD_REMOVE_USER_FROM_TEAM),
         InlineKeyboardButton("➕ " + "افزودن کاربر از تیم های دیگه", callback_data=HEAD_ADD_USER_FROM_OTHER_TEAMS)],
        [get_back_to_menu_button()]
    ])

    await message_sender(text="🎛️ " + "لیست کارای هدی", reply_markup=keyboard)

    return HeadStates.HEAD_ACTION_DECIDER


async def prompt_add_task(update: Update, ctx: ContextTypes, message_sender):
    keyboard = InlineKeyboardMarkup(
        [[InlineKeyboardButton("ساخت فایلش", web_app={"url": "http://localhost:5173/"})],
         *get_head_common_keyboard(return_keyboard=False)]
    )

    await message_sender("خب برای من یه فایل json با ساختار مناسب بفرست", reply_markup=keyboard)

    return HeadStates.HEAD_ADD_TASK


async def add_task(update: Update, ctx: ContextTypes, message_sender):
    user_id = update.effective_user.id

    head = await db.user.find_unique(
        where={
            "tel_id": user_id
        }
    )

    """
    the json file schema should follow
    [
        {
            "username": "GGBoy313",
            "tasks": [
                {
                    "job": "",
                    "weight": 3.25,
                    "deadline": 3
                }
            ]
        }
    ]
    """
    file = await update.message.document.get_file()
    parsed_file = json.loads(await file.download_as_bytearray())

    keyboard = get_head_common_keyboard()

    if not task_validator(parsed_file):
        await update.message.delete()

        await message_sender("فایلی که فرستادی از ساختار درست پیروی نمی کرد دوباره تلاش کن", reply_markup=keyboard)

        return HeadStates.HEAD_ADD_TASK

    await add_task_handler(parsed_file, head.team)

    await message_sender(text="تسک هایی که می خواستی ساخته شد", reply_markup=keyboard, edit=False)


async def show_marked_tasks(update: Update, ctx: ContextTypes.DEFAULT_TYPE, message_sender):
    user_id = update.effective_user.id

    head = await db.user.find_unique(
        where={
            "tel_id": user_id,
        }
    )

    tasks = await db.task.find_many(
        where={
            "team": head.team,
            "approved": False,
            "mark_done": True,
        },
        include={
            "user": True
        }
    )

    keyboard_buttons = list(
        map(
            lambda t: [InlineKeyboardButton(
                f"{t.job} - {t.user.name} - {t.user.nickname}", callback_data=f"{HEAD_APPROVE_TASK_PREFIX} {t.id}")], tasks
        )) + get_head_common_keyboard(return_keyboard=False)

    await message_sender(text="لیست تسک هایی که بچه های تیمت مارک کردن", reply_markup=InlineKeyboardMarkup(keyboard_buttons))


async def approve_task(update: Update, ctx: ContextTypes.DEFAULT_TYPE, message_sender):
    notification_sender = send_notification(update, ctx)

    task_id = int(update.callback_query.data.split(" ")[1])

    task = await db.task.update(
        where={
            "id": task_id
        },
        data={
            "approved": True
        },
        include={
            "user": True
        }
    )

    await notification_sender(text=f"عالی، هد تیمت تسک \"{task.job}\" رو تایید کرد، برو حالشو ببر.", user_id=task.user.tel_id)

    await message_sender(text="آفرین، تسکی که می خواستی تایید شد",
                         reply_markup=get_head_common_keyboard(
                             prev_menu_callback=HEAD_SHOW_MARKED_TASKS,
                             prev_menu_text="✅ " + "بازگشت به منوی تایید تسک"
                         ))

    return HeadStates.HEAD_ACTION_DECIDER


async def show_tasks_to_remove(update: Update, ctx: ContextTypes, message_sender):
    user_id = update.effective_user.id

    head = await db.user.find_unique(
        where={
            "tel_id": user_id
        }
    )

    tasks = await db.task.find_many(
        where={
            "team": head.team,
            "mark_done": False,
            "approved": False,

            "deadline": {
                "gte": datetime.now()
            }
        },
        include={
            "user": True
        }
    )

    keyboard_buttons = list(
        map(
            lambda t: [InlineKeyboardButton(f"{t.job} - {t.user.name} - {t.user.nickname}",
                                            callback_data=f"{HEAD_REMOVE_TASK_PREFIX} {t.id}")], tasks
        )) + get_head_common_keyboard(return_keyboard=False)

    await message_sender(text="لیست تسک هایی که میتونی حذف کنی", reply_markup=InlineKeyboardMarkup(keyboard_buttons))

    return HeadStates.HEAD_ACTION_DECIDER


async def remove_task(update: Update, ctx: ContextTypes.DEFAULT_TYPE, message_sender):
    notification_sender = send_notification(update, ctx)

    task_id = int(update.callback_query.data.split(" ")[1])

    task = await db.task.delete(
        where={
            "id": task_id
        },
        include={
            "user": True
        }
    )

    await notification_sender(
        text=f"کاربر عزیز هد تیمت تسک \"{task.job}\" رو برات حذف کرد برو حالشو ببر.",
        user_id=task.user.tel_id
    )

    await message_sender(text="تسکی که می خواستی حذف شد", reply_markup=get_head_common_keyboard(
        prev_menu_callback=HEAD_SHOW_TASKS_TO_REMOVE,
        prev_menu_text="❌ " + "بازگشت به منوی حذف تسک"
    ))

    return HeadStates.HEAD_ACTION_DECIDER


def show_questions_box_to_remove(for_admin: bool):
    async def show_questions_box_to_remove_action(update: Update, ctx: ContextTypes.DEFAULT_TYPE, _):
        await send_question_boxes(update, ctx, for_admin, title="لیست تمام آزمون هایی که در حال برگزاری هست", prefix=REMOVE_QUESTION_BOX_PREFIX)

        if for_admin:
            return AdminStates.ADMIN_ACTIONS
        else:
            return HeadStates.HEAD_ACTION_DECIDER

    return show_questions_box_to_remove_action


def remove_question_box(for_admin: bool):
    async def remove_question_box_action(update: Update, ctx: ContextTypes.DEFAULT_TYPE, message_sender):
        user_id = update.effective_user.id
        question_box_id = int(update.callback_query.data.split(" ")[1])

        where_options = {
            "id": question_box_id,
        }

        if not for_admin:
            head = await db.user.find_unique(
                where={
                    "tel_id": user_id
                }
            )

            where_options["team"] = head.team

        await db.questionsbox.delete_many(
            where=where_options)

        await message_sender(text="آزمونی که می خواستی حذف شد",
                             reply_markup=get_head_common_keyboard(
                                 prev_menu_callback=HEAD_SHOW_QUESTIONS_BOX_TO_REMOVE,
                                 prev_menu_text="❌❓ " + "بازگشت به منوی حذف آزمون",
                                 for_admin=for_admin
                             ))

        if for_admin:
            return AdminStates.ADMIN_ACTIONS
        else:
            return HeadStates.HEAD_ACTION_DECIDER

    return remove_question_box_action


def show_question_boxes_for_stat(for_admin: bool):
    async def show_question_boxes_for_stat_action(update: Update, ctx: ContextTypes.DEFAULT_TYPE, _):
        await send_question_boxes(update, ctx, for_admin, title="تمام آزمون هایی که میتونی وضعیتشو ببینی", prefix=GET_QUESTION_BOX_STAT_PREFIX)

        if for_admin:
            return AdminStates.ADMIN_ACTIONS
        else:
            return HeadStates.HEAD_ACTION_DECIDER

    return show_question_boxes_for_stat_action


def show_question_box_stat_and_percent(for_admin: bool):
    async def show_question_box_stat_action(update: Update, ctx: ContextTypes.DEFAULT_TYPE, message_sender):
        user_id = update.effective_user.id
        question_box_id = int(update.callback_query.data.split(" ")[1])

        where_options = {
            "id": question_box_id,
        }

        if not for_admin:
            head = await db.user.find_unique(
                where={
                    "tel_id": user_id
                }
            )

            where_options["team"] = head.team

        question_box = await db.questionsbox.find_first(
            where=where_options,
            include={
                "questions": {
                    "include": {
                        "options": True,
                        "c_users": True,
                        "w_users": True
                    },
                }
            }
        )

        text = f"وضعیت آزمون {question_box.label}\n\n"

        for question in question_box.questions:
            correct_answers = len(question.c_users)
            wrong_answers = len(question.w_users)
            total_answers = correct_answers + wrong_answers
            correct_answers_percent = str((
                correct_answers / total_answers) * 100) + "%" if total_answers > 0 else "نا معلوم"
            wrong_answers_percent = str((
                wrong_answers / total_answers) * 100) + "%" if total_answers > 0 else "نا معلوم"

            text += (
                f"سوال {question.question}\n"
                f"درصد افرادی که درست جواب دادند: {correct_answers_percent}\n"
                f"درصد افرادی که غلط جواب دادند: {wrong_answers_percent}\n\n"
                "---------------------------------------------------------------\n\n"
            )

        await message_sender(text=text, reply_markup=get_head_common_keyboard(
            prev_menu_callback=HEAD_SHOW_QUESTION_BOXES_FOR_STAT,
            prev_menu_text="💯 " + "بازگشت به منوی وضعیت آزمون",
            for_admin=for_admin
        ))

        if for_admin:
            return AdminStates.ADMIN_ACTIONS
        else:
            return HeadStates.HEAD_ACTION_DECIDER

    return show_question_box_stat_action


async def see_team_users_list(update: Update, ctx: ContextTypes.DEFAULT_TYPE, message_sender):
    user_id = update.effective_user.id

    head = await get_user(user_id)

    team_members = await db.user.find_many(
        where={
            "OR": [
                {
                    "team": head.team
                },
                {
                    "secondary_teams": {
                        "has": head.team
                    }
                }
            ]
        }
    )

    team_members_template = ""

    for i, user in enumerate(team_members):
        team_members_template += show_user(user.name, user.nickname, user.student_code,
                                           user.role, i + 1)

    await message_sender(text=team_members_template, reply_markup=get_head_common_keyboard())

    return HeadStates.HEAD_ACTION_DECIDER


async def show_teams_to_add_team_member(update: Update, ctx: ContextTypes.DEFAULT_TYPE, message_sender):
    keyboard = InlineKeyboardMarkup(
        get_teams_keyboard(
            HEAD_SHOW_USERS_TO_MEMBER_ADD_FROM_OTHER_TEAM_PREFIX, return_keyboard=False, include_cancel_button=False) +
        get_head_common_keyboard(return_keyboard=False))

    await message_sender(text="از کدوم تیم می خوای اضافه کنی؟", reply_markup=keyboard)

    return HeadStates.HEAD_ACTION_DECIDER


async def show_users_to_add_member_from_other_team(update: Update, ctx: ContextTypes.DEFAULT_TYPE, message_sender):
    callback_team = update.callback_query.data.split(" ")[1]
    target_team = None

    for team in Team:
        if callback_team == team.value:
            target_team = team.value
            break

    users = await db.user.find_many(
        where={
            "OR": [
                {
                    "team": target_team
                },
                {
                    "secondary_teams": {
                        "has": target_team
                    }
                }
            ]
        }
    )

    keyboard = InlineKeyboardMarkup(
        list(map(lambda u: [InlineKeyboardButton(show_user(
            u.name, u.nickname, u.student_code, u.role, ignore_trailing_dashes=True), callback_data=f"{HEAD_ADD_MEMBER_FROM_OTHER_TEAMS_PREFIX} {u.id}")], users)) +
        get_head_common_keyboard(
            prev_menu_callback=HEAD_ADD_USER_FROM_OTHER_TEAMS,
            prev_menu_text="بازگشت به منوی افزودن از تیم های دیگه",
            return_keyboard=False
        )
    )

    await message_sender(text="خب حالا کدوم کاربر از این تیمی که انتخاب کردی رو می خوای وارد تیمت کنی؟", reply_markup=keyboard)

    return HeadStates.HEAD_ACTION_DECIDER


async def add_team_member_from_other_teams(update: Update, ctx: ContextTypes.DEFAULT_TYPE, message_sender):
    user_id = update.effective_user.id

    memeber_id = int(update.callback_query.data.split(" ")[1])

    head = await get_user(user_id)

    await db.user.update(
        where={
            "id": memeber_id
        },
        data={
            "secondary_teams": {
                "push": head.team
            }
        }
    )

    keyboard = get_head_common_keyboard(
        prev_menu_callback=HEAD_ADD_USER_FROM_OTHER_TEAMS,
        prev_menu_text="بازگشت به منوی افزودن از تیم های دیگه"
    )

    await message_sender(text="کاربری که می خواستی به تیمت اضافه شد", reply_markup=keyboard)

    return HeadStates.HEAD_ACTION_DECIDER


async def show_users_list_to_remove_from_team(update: Update, ctx: ContextTypes.DEFAULT_TYPE, message_sender):
    user_id = update.effective_user.id

    head = await get_user(user_id)

    users = await db.user.find_many(
        where={
            "OR": [
                {
                    "team": head.team
                },
                {
                    "secondary_teams": {
                        "has": head.team
                    }
                }
            ],
            "NOT": {
                "OR": [
                   {
                       "role": UserRole.ADMIN
                   },
                    {
                       "role": UserRole.HEAD
                   }
                ]
            }
        }
    )

    keyboard = InlineKeyboardMarkup(
        list(map(lambda u: [InlineKeyboardButton(show_user(
            u.name, u.nickname, u.student_code, u.role, ignore_trailing_dashes=True), callback_data=f"{HEAD_REMOVE_TEAM_MEMBER_PREFIX} {u.tel_id}")], users)) +
        get_head_common_keyboard(return_keyboard=False)
    )

    await message_sender(text="کدوم یکی از اعضای تیمت رو می خوای حذف کنی؟", reply_markup=keyboard)

    return HeadStates.HEAD_ACTION_DECIDER


async def remove_team_member(update: Update, ctx: ContextTypes.DEFAULT_TYPE, message_sender):
    user_id = update.effective_user.id

    member_id = int(update.callback_query.data.split(" ")[1])

    head = await get_user(user_id)
    member = await get_user(member_id)

    if member.team == head.team:
        await db.user.update(
            where={
                "id": member_id
            },
            data={
                "team": Team.NO_TEAM
            }
        )
    else:
        secondary_teams = member.secondary_teams.copy()
        secondary_teams.remove(head.team)

        await db.user.update(
            where={
                "tel_id": member_id
            },
            data={
                "secondary_teams": {
                    "set": secondary_teams
                }
            }
        )

    await message_sender(text="کاربر از تیمت حذف شد", reply_markup=get_head_common_keyboard())

    return HeadStates.HEAD_ACTION_DECIDER
