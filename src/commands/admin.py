from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, ConversationHandler
from datetime import datetime, timedelta
from prisma.enums import UserRole
import json

from src.utils.db import db
from src.utils.is_there_admin import is_there_admin
from src.utils.ignore_command import ignore_command
from src.utils.ignore_user import ignore_user
from src.utils.show_user import show_user
from src.utils.get_back_to_menu_button import get_back_to_menu_button
from src.utils.send_message import send_message
from src.utils.get_users_keyboard import get_users_keyboard
from src.utils.is_admin import is_admin
from src.constants.commands import REGISTER_ADMIN
from src.constants.states import AdminStates
from src.constants.commands import ADMIN_SHOW_USERS_LIST, BACK_TO_ADMIN_ACTIONS, ADMIN_PROMPT_ADD_QUESTION_BOX, ADMIN_ADD_HEAD, ADMIN_SHOW_USERS_LIST_BUTTONS


async def show_admin_actions(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    should_ignore = await ignore_user(update, ctx)
    is_there_any_admin = await is_there_admin()
    is_user_admin = await is_admin(update, ctx)
    message_sender = send_message(update, ctx)
    message = update.message

    if message:
        await message.delete()

    if should_ignore:
        return ConversationHandler.END

    if is_there_any_admin and (not is_user_admin):
        await ignore_command(update, ctx)
        return ConversationHandler.END

    keyboard_buttons = []

    if not is_there_any_admin:
        keyboard_buttons.append(InlineKeyboardButton(
            "ثبت به عنوان ادمین", callback_data=REGISTER_ADMIN))

        await message_sender(text="ادمینی وجود ندارد بدو ثبت کن خودتو هرچه زودتر", reply_markup=InlineKeyboardMarkup([keyboard_buttons]))

        return AdminStates.REGISTER_USER_AS_AN_ADMIN

    keyboard_buttons.append(
        InlineKeyboardButton("➕ " + "افزودن آزمون",
                             callback_data=ADMIN_PROMPT_ADD_QUESTION_BOX)
    )

    keyboard_buttons.append(
        InlineKeyboardButton("📃 " + "نمایش لیست کاربران",
                             callback_data=ADMIN_SHOW_USERS_LIST)
    )

    keyboard = InlineKeyboardMarkup(
        [
            keyboard_buttons,
            [InlineKeyboardButton("🧑‍💼 " + "افزودن هد",
                                  callback_data=ADMIN_SHOW_USERS_LIST_BUTTONS)],
            [get_back_to_menu_button()]
        ]
    )

    await message_sender(text="🧑‍💼 " + "لیست کارای ادمینی", reply_markup=keyboard)

    return AdminStates.ADMIN_ACTIONS


async def register_admin(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    should_ignore = await ignore_user(update, ctx)
    is_there_any_admin = await is_there_admin()
    message_sender = send_message(update, ctx)

    if should_ignore or is_there_any_admin:
        return ConversationHandler.END

    user_id = update.effective_user.id

    await db.user.update(
        where={
            "tel_id": user_id
        },
        data={
            "role": UserRole.ADMIN
        }
    )

    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "بازگشت به لیست کارای ادمینی", callback_data=BACK_TO_ADMIN_ACTIONS),
                get_back_to_menu_button()
            ]
        ]
    )

    await message_sender(text="حسابت به عنوان ادمین ثبت شد", reply_markup=keyboard)

    return AdminStates.SHOW_ADMIN_ACTIONS


async def add_question_box(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    should_ignore = await ignore_command(update, ctx)
    message_sender = send_message(update, ctx)

    if should_ignore:
        return ConversationHandler.END

    callback_query = update.callback_query

    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "بازگشت به لیست کارای ادمینی", callback_data=BACK_TO_ADMIN_ACTIONS),
                get_back_to_menu_button()
            ]
        ]
    )

    if callback_query:
        await message_sender(text="برا من یه فایل json بفرست که مطابق schema درست باشه", reply_markup=keyboard)

        return AdminStates.ADMIN_ACTIONS

    file = await update.message.document.get_file()

    """
    json that is sent to bot should follow these structures:
        {
            "label": str,
            "duration": int,
            "deadline": int,
            "team": one of team enum value,
            "questions": [
              {
                "label": str,
                "score", int,
                "options": [
                    {
                        "label": str,
                        "is_answer": bool,
                    }
                ]
              }
            ]
        }

        at least one question with four answers minimum is required
    """
    parsed_file = json.loads(await file.download_as_bytearray())

    # deadline is the number of days from now which this line is making that time with timestamp
    real_deadline = datetime.now(
    ) + timedelta(days=int(parsed_file["duration"]))

    question_box = await db.questionsbox.create(
        data={
            "label": parsed_file["label"],
            "duration": int(parsed_file["duration"]),
            "deadline": real_deadline,
            "team": parsed_file["team"]
        }
    )

    for question in parsed_file["questions"]:
        await db.question.create(
            data={
                "question": question["label"],
                "score": question["score"],
                "options": {
                    "create": list(map(lambda option: {
                        "label": option["label"],
                        "is_answer": option["is_answer"]
                    }, question["options"]))
                },
                "question_box": {
                    "connect": {
                        "id": question_box.id
                    }
                }
            }
        )

    await message_sender(text="نه بابا، آزمونتو ساختی داپش", reply_markup=keyboard, edit=False)

    return AdminStates.SHOW_ADMIN_ACTIONS


async def show_users_list(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    should_ignore = await ignore_command(update, ctx)
    message_sender = send_message(update, ctx)

    if should_ignore:
        return ConversationHandler.END

    users = await db.user.find_many(where={
        "NOT": {
            "role": UserRole.ADMIN
        }
    })

    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "بازگشت به لیست کارای ادمینی", callback_data=BACK_TO_ADMIN_ACTIONS),
                get_back_to_menu_button()
            ]
        ]
    )

    users_template = ""

    for i, user in enumerate(users):
        users_template += show_user(user.nickname, user.student_code,
                                    user.role, i + 1)

    await message_sender(text=users_template, reply_markup=keyboard)

    return AdminStates.ADMIN_ACTIONS


async def show_users_list_buttons(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    message_sender = send_message(update, ctx)

    await message_sender(text="کدوم کاربر رو میخوای هد کنی؟", reply_markup=await get_users_keyboard(exclude_heads=True))

    return AdminStates.ADD_HEAD


async def admin_decider(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    return AdminStates.ADD_HEAD


async def add_head(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user_id = int(update.callback_query.data)
    message_sender = send_message(update, ctx)

    await db.user.update(
        where={
            "id": user_id
        },
        data={
            "role": UserRole.HEAD
        }
    )

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "بازگشت به لیست کارای ادمینی", callback_data=BACK_TO_ADMIN_ACTIONS),
            get_back_to_menu_button()
        ]

    ])

    await message_sender(text="خب این یارو رو هد کردی، ماشالا", reply_markup=keyboard)

    return AdminStates.SHOW_ADMIN_ACTIONS
