from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, ConversationHandler
from datetime import datetime
import pytz

from src.utils.db import db
from src.utils.get_tasks_keyboard import get_tasks_keyboard
from src.utils.send_message import send_message
from src.utils.get_back_to_menu_button import get_back_to_menu_button
from src.utils.send_notification import send_notification
from src.utils.get_jalali import get_jalali
from src.utils.ignore_none_registered import ignore_none_registered
from src.utils.get_user import get_user
from src.constants.states import TaskStates
from src.constants.commands import REMAINING_TASKS, DONE_TASKS, TOTAL_TASKS_SCORE,\
    BACK_TO_TASKS_ACTIONS, SUBMIT_TASK


async def show_tasks_actions(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    should_ignore = await ignore_none_registered(update, ctx)
    message_sender = send_message(update, ctx)

    if should_ignore:
        return ConversationHandler.END

    keyboard = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("📃 " + "تسک هایی که دارای",
                                  callback_data=REMAINING_TASKS)],
            [InlineKeyboardButton("➕ " + "ثبت انجام تسک",
                                  callback_data=SUBMIT_TASK)],
            [InlineKeyboardButton("✅ " + "تسک هایی که انجام دادی",
                                  callback_data=DONE_TASKS)],
            [InlineKeyboardButton("🔢 " + "مجموع امتیازات تا الان",
                                  callback_data=TOTAL_TASKS_SCORE)],
            [get_back_to_menu_button()]
        ]
    )

    await message_sender(text="لیست کارایی که میتونی انجام بدی", reply_markup=keyboard)

    return TaskStates.TASK_ACTION_DECIDER


def show_remaining_tasks(prefix: str, text: str, without_mark: bool):
    async def show_remaining_tasks_actions(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        should_ignore = await ignore_none_registered(update, ctx)
        message_sender = send_message(update, ctx)

        if should_ignore:
            return ConversationHandler.END

        (keyboard, is_there_any_tasks) = await get_tasks_keyboard(user_id, prefix, without_mark)

        if is_there_any_tasks:
            await message_sender(text=text, reply_markup=keyboard)
        else:
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton(
                    "⏮️ " + "بازگشت به منوی تسک ها", callback_data=BACK_TO_TASKS_ACTIONS)],
                [get_back_to_menu_button()]])
            await message_sender(text="آفرین، فعلا تسکی برای انجام نمونده", reply_markup=keyboard)

        return TaskStates.TASK_ACTION_DECIDER

    return show_remaining_tasks_actions


async def show_task_information(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    # the first element is the constant prefix but the second element is the task id
    task_id = int(update.callback_query.data.split(" ")[1])
    should_ignore = await ignore_none_registered(update, ctx)
    message_sender = send_message(update, ctx)

    if should_ignore:
        return ConversationHandler.END

    task = await db.task.find_unique(
        where={
            "id": task_id
        }
    )

    time_delta = (task.deadline.replace(
        tzinfo=pytz.utc) - datetime.now(tz=pytz.utc))
    left_days = time_delta.days
    left_hours = time_delta.seconds // 3600

    left_time = ""

    if left_days > 0:
        left_time += f"{left_days} روز"

    if left_hours > 0:
        if left_days > 0:
            left_time += " و "
        left_time += f"{left_hours} ساعت"

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(
            "⏮️ " + "بازگشت به منوی تسک ها", callback_data=BACK_TO_TASKS_ACTIONS)],
        [get_back_to_menu_button()]
    ])

    text = (
        "جزییات تسک \n\n"
        f"تیم مربوطه: {task.team}\n\n"
        f"تسک: {task.job}\n\n"
        f"وزن کار: {task.weight}\n\n"
        f"مهلت باقی مونده: {left_time}\n\n"
        f"تاریخ ددلاین: {get_jalali(task.deadline)}\n\n"
    )

    await message_sender(text=text, reply_markup=keyboard)

    return TaskStates.TASK_ACTION_DECIDER


async def show_done_tasks(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    should_ignore = await ignore_none_registered(update, ctx)
    message_sender = send_message(update, ctx)

    if should_ignore:
        return ConversationHandler.END

    tasks = await db.task.find_many(
        where={
            "approved": True,
            "user": {
                "tel_id": user_id
            }
        },
        order={
            "created_at": "desc"
        }
    )

    template = ""

    if len(tasks) != 0:
        template += "لیست تسک هایی که تا الان انجام دادی\n\n"

        for task in tasks:
            template += f"{task.job}\n\n ----------------------------------------------\n\n"
    else:
        template = "تسکی تا حالا انجام ندادی 😔"

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(
            "⏮️ " + "بازگشت به منوی تسک ها", callback_data=BACK_TO_TASKS_ACTIONS)],
        [get_back_to_menu_button()]
    ])

    await message_sender(text=template, reply_markup=keyboard)

    return TaskStates.TASK_ACTION_DECIDER


async def show_tasks_total_score(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    should_ignore = await ignore_none_registered(update, ctx)
    message_sender = send_message(update, ctx)

    if should_ignore:
        return ConversationHandler.END

    # this way put pressure on code
    # TODO: change this to aggregation for calculating total score
    tasks = await db.task.find_many(
        where={
            "approved": True,
            "user": {
                "tel_id": user_id
            }
        }
    )

    total_score = 0

    for task in tasks:
        total_score += task.weight

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(
            "⏮️ " + "بازگشت به منوی تسک ها", callback_data=BACK_TO_TASKS_ACTIONS)],
        [get_back_to_menu_button()]
    ])

    text = (
        "💯 "
        "مجموع امتیازاتی که از انجام دادن تسک ها بدست آوردی:\n\n"
        f"{total_score} امتیاز"
    )

    await message_sender(text=text, reply_markup=keyboard)

    return TaskStates.TASK_ACTION_DECIDER


async def mark_task(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    task_id = int(update.callback_query.data.split(" ")[1])
    should_ignore = await ignore_none_registered(update, ctx)
    message_sender = send_message(update, ctx)
    notification_sender = send_notification(update, ctx)

    if should_ignore:
        return ConversationHandler.END

    task = await db.task.update(
        where={
            "id": task_id
        },
        data={
            "mark_done": True
        }
    )

    user = await get_user(user_id)

    await notification_sender(text=f"هد عزیز نوچه {user.nickname} تسک \"{task.job}\" رو مارک کردن برو اگه درسته تاییدش کن", team=task.team)

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(
            "⏮️ " + "بازگشت به منوی تسک ها", callback_data=BACK_TO_TASKS_ACTIONS)],
        [get_back_to_menu_button()]
    ])

    await message_sender(text="عالی، به اطلاع هد تیمت میرسونیم که تسک رو انجام دادی", reply_markup=keyboard)

    return TaskStates.TASK_ACTION_DECIDER
