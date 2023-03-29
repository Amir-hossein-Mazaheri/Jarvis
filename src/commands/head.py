from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, ConversationHandler
from datetime import datetime, timedelta
import json

from src.utils.db import db
from src.utils.send_message import send_message
from src.utils.ignore_none_head import ignore_none_head
from src.utils.get_back_to_menu_button import get_back_to_menu_button
from src.utils.task_validator import task_validator
from src.utils.ignore_command import ignore_command
from src.utils.send_question_boxes import send_question_boxes
from src.constants.states import HeadStates, AdminStates
from src.constants.commands import ADMIN_PROMPT_ADD_QUESTION_BOX, HEAD_ADD_TASK,\
    BACK_TO_HEAD_ACTIONS, HEAD_APPROVE_TASK, HEAD_SHOW_MARKED_TASKS, HEAD_SHOW_TASKS_TO_REMOVE,\
    HEAD_REMOVE_TASK, REMOVE_QUESTION_BOX_PREFIX, BACK_TO_ADMIN_ACTIONS, HEAD_SHOW_QUESTIONS_BOX_TO_REMOVE, \
    GET_QUESTION_BOX_STAT_PREFIX, HEAD_SHOW_QUESTION_BOXES_FOR_STAT


async def show_head_actions(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    should_ignore = await ignore_none_head(update, ctx)
    message_sender = send_message(update, ctx)

    if should_ignore:
        return ConversationHandler.END

    questions_box_buttons = [InlineKeyboardButton(
        "❓ " + "افزودن آزمون", callback_data=ADMIN_PROMPT_ADD_QUESTION_BOX),
        InlineKeyboardButton("💯 " + "وضعیت آزمون ها",
                             callback_data=HEAD_SHOW_QUESTION_BOXES_FOR_STAT),
        InlineKeyboardButton("❌❓ " + "حذف آزمون",
                             callback_data=HEAD_SHOW_QUESTIONS_BOX_TO_REMOVE),
    ]

    questions_box_buttons.reverse()

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("⚒️ " + "افزودن تسک",
                              callback_data=HEAD_ADD_TASK), InlineKeyboardButton("❌ " + "حذف تسک", callback_data=HEAD_SHOW_TASKS_TO_REMOVE)],
        questions_box_buttons,
        [InlineKeyboardButton("✅ " + "تایید تسک های تیمت",
                              callback_data=HEAD_SHOW_MARKED_TASKS)],
        [get_back_to_menu_button()]
    ])

    await message_sender(text="🎛️ " + "لیست کارای هدی", reply_markup=keyboard)

    return HeadStates.HEAD_ACTION_DECIDER


async def prompt_add_task(update: Update, ctx: ContextTypes):
    should_ignore = await ignore_none_head(update, ctx)
    message_sender = send_message(update, ctx)

    if should_ignore:
        return ConversationHandler.END

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(
            "🎛️ " + "بازگشت به منوی کارای هدی", callback_data=BACK_TO_HEAD_ACTIONS)],
        [get_back_to_menu_button()]
    ])

    await message_sender("خب برای من یه فایل json با ساختار مناسب بفرست", reply_markup=keyboard)

    return HeadStates.HEAD_ADD_TASK


async def add_task(update: Update, ctx: ContextTypes):
    user_id = update.effective_user.id
    should_ignore = await ignore_none_head(update, ctx)
    message_sender = send_message(update, ctx)

    if should_ignore:
        return ConversationHandler.END

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

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(
            "🎛️ " + "بازگشت به منوی کارای هدی", callback_data=BACK_TO_HEAD_ACTIONS)],
        [get_back_to_menu_button()]
    ])

    if not task_validator(parsed_file):
        await update.message.delete()

        await message_sender("فایلی که فرستادی از ساختار درست پیروی نمی کرد دوباره تلاش کن", reply_markup=keyboard)

        return HeadStates.HEAD_ADD_TASK

    async with db.batch_() as batcher:
        for user_info in parsed_file:
            user = await db.user.find_first(
                where={
                    "name": "@" + user_info["username"],
                    "team": head.team
                }
            )

            if not bool(user):
                continue

            for task in user_info["tasks"]:
                deadline = datetime.now() + \
                    timedelta(days=int(task["deadline"]))

                await batcher.task.create(
                    data={
                        "job": task["job"],
                        "weight": task["weight"],
                        "deadline": deadline,
                        "team": head.team,

                        "user": {
                            "connect": {
                                "id": user.id
                            }
                        }
                    }
                )

    await message_sender(text="تسک هایی که می خواستی ساخته شد", reply_markup=keyboard, edit=False)


async def show_marked_tasks(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    should_ignore = await ignore_none_head(update, ctx)
    message_sender = send_message(update, ctx)

    if should_ignore:
        return ConversationHandler.END

    head = await db.user.find_unique(
        where={
            "tel_id": user_id,
        }
    )

    tasks = await db.task.find_many(
        where={
            "team": head.team,
            "approved": False,
            "markDone": True,
        },
        include={
            "user": True
        }
    )

    keyboard_buttons = list(map(lambda t: [InlineKeyboardButton(
        f"{t.job} - {t.user.name} - {t.user.nickname}", callback_data=f"{HEAD_APPROVE_TASK} {t.id}")], tasks))

    keyboard_buttons.append([
        InlineKeyboardButton(
            "🎛️ " + "بازگشت به منوی کارای هدی", callback_data=BACK_TO_HEAD_ACTIONS)
    ])

    keyboard_buttons.append(
        [get_back_to_menu_button()]
    )

    await message_sender(text="لیست تسک هایی که بچه های تیمت مارک کردن", reply_markup=InlineKeyboardMarkup(keyboard_buttons))


async def approve_task(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    should_ignore = await ignore_none_head(update, ctx)
    message_sender = send_message(update, ctx)

    if should_ignore:
        return ConversationHandler.END

    task_id = int(update.callback_query.data.split(" ")[1])

    await db.task.update(
        where={
            "id": task_id
        },
        data={
            "approved": True
        }
    )

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ " + "بازگشت به منوی تایید تسک",
                              callback_data=HEAD_SHOW_MARKED_TASKS)],
        [InlineKeyboardButton(
            "🎛️ " + "بازگشت به منوی کارای هدی", callback_data=BACK_TO_HEAD_ACTIONS)],
        [get_back_to_menu_button()]
    ])

    await message_sender(text="آفرین، تسکی که می خواستی تایید شد", reply_markup=keyboard)

    return HeadStates.HEAD_ACTION_DECIDER


async def show_tasks_to_remove(update: Update, ctx: ContextTypes):
    user_id = update.effective_user.id
    should_ignore = await ignore_none_head(update, ctx)
    message_sender = send_message(update, ctx)

    if should_ignore:
        return ConversationHandler.END

    head = await db.user.find_unique(
        where={
            "tel_id": user_id
        }
    )

    tasks = await db.task.find_many(
        where={
            "team": head.team,
            "markDone": False,
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
        map(lambda t: [InlineKeyboardButton(f"{t.job} - {t.user.name} - {t.user.nickname}", callback_data=f"{HEAD_REMOVE_TASK} {t.id}")], tasks))

    keyboard_buttons.append(
        [InlineKeyboardButton(
            "🎛️ " + "بازگشت به منوی کارای هدی", callback_data=BACK_TO_HEAD_ACTIONS)],
    )

    keyboard_buttons.append(
        [get_back_to_menu_button()]
    )

    await message_sender(text="لیست تسک هایی که میتونی حذف کنی", reply_markup=InlineKeyboardMarkup(keyboard_buttons))

    return HeadStates.HEAD_ACTION_DECIDER


async def remove_task(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    should_ignore = await ignore_none_head(update, ctx)
    message_sender = send_message(update, ctx)

    if should_ignore:
        return ConversationHandler.END

    task_id = int(update.callback_query.data.split(" ")[1])

    await db.task.delete(
        where={
            "id": task_id
        }
    )

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(
            "❌ " + "بازگشت به منوی حذف تسک", callback_data=HEAD_SHOW_TASKS_TO_REMOVE)],
        [InlineKeyboardButton(
            "🎛️ " + "بازگشت به منوی کارای هدی", callback_data=BACK_TO_HEAD_ACTIONS)],
        [get_back_to_menu_button()]
    ])

    await message_sender(text="تسکی که می خواستی حذف شد", reply_markup=keyboard)

    return HeadStates.HEAD_ACTION_DECIDER


def show_questions_box_to_remove(for_admin: bool):
    async def show_questions_box_to_remove_action(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        should_ignore = await ignore_none_head(update, ctx)

        if should_ignore:
            return ConversationHandler.END

        await send_question_boxes(update, ctx, for_admin, title="لیست تمام آزمون هایی که در حال برگزاری هست", prefix=REMOVE_QUESTION_BOX_PREFIX)

        if for_admin:
            return AdminStates.ADMIN_ACTIONS
        else:
            return HeadStates.HEAD_ACTION_DECIDER

    return show_questions_box_to_remove_action


def remove_question_box(for_admin: bool):
    async def remove_question_box_action(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        should_ignore = await ignore_command(update, ctx) if for_admin else await ignore_none_head(update, ctx)
        message_sender = send_message(update, ctx)

        if should_ignore:
            return ConversationHandler.END

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

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(
                "❌❓ " + "بازگشت به منوی حذف آزمون", callback_data=HEAD_SHOW_QUESTIONS_BOX_TO_REMOVE)],
            [InlineKeyboardButton(
                "بازگشت به لیست کارای ادمینی", callback_data=BACK_TO_ADMIN_ACTIONS)] if for_admin else [InlineKeyboardButton(
                    "🎛️ " + "بازگشت به منوی کارای هدی", callback_data=BACK_TO_HEAD_ACTIONS)],
            [get_back_to_menu_button()]
        ])

        await message_sender(text="آزمونی که می خواستی حذف شد", reply_markup=keyboard)

        if for_admin:
            return AdminStates.ADMIN_ACTIONS
        else:
            return HeadStates.HEAD_ACTION_DECIDER

    return remove_question_box_action


def show_question_boxes_for_stat(for_admin: bool):
    async def show_question_boxes_for_stat_action(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        should_ignore = await ignore_none_head(update, ctx)

        if should_ignore:
            return ConversationHandler.END

        await send_question_boxes(update, ctx, for_admin, title="تمام آزمون هایی که میتونی وضعیتشو ببینی", prefix=GET_QUESTION_BOX_STAT_PREFIX)

        if for_admin:
            return AdminStates.ADMIN_ACTIONS
        else:
            return HeadStates.HEAD_ACTION_DECIDER

    return show_question_boxes_for_stat_action


def show_question_box_stat_and_percent(for_admin: bool):
    async def show_question_box_stat_action(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        should_ignore = await ignore_command(update, ctx) if for_admin else await ignore_none_head(update, ctx)
        message_sender = send_message(update, ctx)

        if should_ignore:
            return ConversationHandler.END

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

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("💯 " + "بازگشت به منوی وضعیت آزمون",
                                  callback_data=HEAD_SHOW_QUESTION_BOXES_FOR_STAT)],
            [InlineKeyboardButton(
                "بازگشت به لیست کارای ادمینی", callback_data=BACK_TO_ADMIN_ACTIONS)] if for_admin else [InlineKeyboardButton(
                    "🎛️ " + "بازگشت به منوی کارای هدی", callback_data=BACK_TO_HEAD_ACTIONS)],
            [get_back_to_menu_button()]
        ])

        text = f"وضعیت آزمون {question_box.label}\n\n"

        for question in question_box.questions:
            correct_answers = len(question.c_users)
            wrong_answers = len(question.w_users)
            total_answers = correct_answers + wrong_answers
            correct_answers_percent = (
                correct_answers / total_answers) * 100 if total_answers > 0 else "نا معلوم"
            wrong_answers_percent = (
                wrong_answers / total_answers) * 100 if total_answers > 0 else "نا معلوم"

            text += (
                f"سوال {question.question}\n"
                f"درصد افرادی که درست جواب دادند: {correct_answers_percent}%\n"
                f"درصد افرادی که غلط جواب دادند: {wrong_answers_percent}%\n\n"
                "---------------------------------------------------------------\n\n"
            )

        await message_sender(text=text, reply_markup=keyboard)

        if for_admin:
            return AdminStates.ADMIN_ACTIONS
        else:
            return HeadStates.HEAD_ACTION_DECIDER

    return show_question_box_stat_action
