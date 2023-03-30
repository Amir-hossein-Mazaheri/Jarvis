from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, ConversationHandler
from datetime import datetime, timedelta
from prisma.enums import UserRole
import json

from src.utils.db import db
from src.utils.is_there_admin import is_there_admin
from src.utils.ignore_none_admin import ignore_none_admin
from src.utils.ignore_none_registered import ignore_none_registered
from src.utils.show_user import show_user
from src.utils.get_back_to_menu_button import get_back_to_menu_button
from src.utils.send_message import send_message
from src.utils.get_users_keyboard import get_users_keyboard
from src.utils.is_admin import is_admin
from src.utils.question_box_validator import question_box_validator
from src.utils.ignore_none_head import ignore_none_head
from src.constants.commands import REGISTER_ADMIN
from src.constants.states import AdminStates, HeadStates
from src.constants.commands import ADMIN_SHOW_USERS_LIST, BACK_TO_ADMIN_ACTIONS, ADMIN_PROMPT_ADD_QUESTION_BOX, ADMIN_ADD_HEAD, ADMIN_SHOW_USERS_LIST_BUTTONS, BACK_TO_HEAD_ACTIONS, ADMIN_SHOW_QUESTIONS_BOX_TO_REMOVE, GET_QUESTION_BOX_STAT_PREFIX, ADMIN_SHOW_QUESTION_BOXES_FOR_STAT


async def show_admin_actions(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    should_ignore = await ignore_none_registered(update, ctx)
    is_there_any_admin = await is_there_admin()
    is_user_admin = await is_admin(update, ctx)
    message_sender = send_message(update, ctx)
    message = update.message

    if message:
        await message.delete()

    if should_ignore:
        return ConversationHandler.END

    if is_there_any_admin and (not is_user_admin):
        await ignore_none_admin(update, ctx)
        return ConversationHandler.END

    keyboard_buttons = []

    if not is_there_any_admin:
        keyboard_buttons.append(InlineKeyboardButton(
            "ثبت به عنوان ادمین", callback_data=REGISTER_ADMIN))

        await message_sender(text="ادمینی وجود ندارد بدو ثبت کن خودتو هرچه زودتر", reply_markup=InlineKeyboardMarkup([keyboard_buttons]))

        return AdminStates.REGISTER_USER_AS_AN_ADMIN

    keyboard_buttons.append(
        InlineKeyboardButton("❌❓ " + "حذف آزمون",
                             callback_data=ADMIN_SHOW_QUESTIONS_BOX_TO_REMOVE)
    )

    keyboard_buttons.append(
        InlineKeyboardButton("💯 " + "وضعیت آزمون",
                             callback_data=ADMIN_SHOW_QUESTION_BOXES_FOR_STAT)
    )

    keyboard_buttons.append(
        InlineKeyboardButton("➕ " + "افزودن آزمون",
                             callback_data=ADMIN_PROMPT_ADD_QUESTION_BOX)
    )

    keyboard = InlineKeyboardMarkup(
        [
            keyboard_buttons,
            [InlineKeyboardButton("🧑‍💼 " + "افزودن هد",
                                  callback_data=ADMIN_SHOW_USERS_LIST_BUTTONS)],
            [InlineKeyboardButton("📃 " + "نمایش لیست کاربران",
                                  callback_data=ADMIN_SHOW_USERS_LIST)
             ],
            [get_back_to_menu_button()]
        ]
    )

    await message_sender(text="🧑‍💼 " + "لیست کارای ادمینی", reply_markup=keyboard)

    return AdminStates.ADMIN_ACTIONS


async def register_admin(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    should_ignore = await ignore_none_registered(update, ctx)
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


def add_question_box(for_admin: bool):
    async def add_question_box_action(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        should_ignore = await ignore_none_head(update, ctx)
        message_sender = send_message(update, ctx)

        if should_ignore:
            return ConversationHandler.END

        callback_query = update.callback_query

        keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "بازگشت به لیست کارای ادمینی", callback_data=BACK_TO_ADMIN_ACTIONS) if for_admin else InlineKeyboardButton(
                        "🎛️ " + "بازگشت به منوی کارای هدی", callback_data=BACK_TO_HEAD_ACTIONS),
                    get_back_to_menu_button()
                ]
            ]
        )

        if callback_query:
            await message_sender(text="برا من یه فایل json بفرست که مطابق schema درست باشه", reply_markup=keyboard)

            if for_admin:
                return AdminStates.ADMIN_ACTIONS
            else:
                return HeadStates.HEAD_ACTION_DECIDER

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
        file = await update.message.document.get_file()
        parsed_file = json.loads(await file.download_as_bytearray())

        if not question_box_validator(parsed_file):
            await message_sender(text="فایلی که فرستادی از ساختار درست پیروی نمی کرد، مجدد تلاش کن", reply_markup=keyboard)

            if for_admin:
                return AdminStates.ADMIN_ACTIONS
            else:
                return HeadStates.HEAD_ACTION_DECIDER

        # deadline is the number of days from now which this line is making that time with timestamp
        real_deadline = datetime.now(
        ) + timedelta(days=int(parsed_file["duration"]))

        team = parsed_file["team"]

        if not for_admin:
            head = await db.user.find_unique(
                where={
                    "tel_id": user_id
                }
            )

            team = head.team

        async with db.batch_() as batcher:
            question_box = await db.questionsbox.create(
                data={
                    "label": parsed_file["label"],
                    "duration": int(parsed_file["duration"]),
                    "deadline": real_deadline,
                    "team": team,
                }
            )

            try:
                for question in parsed_file["questions"]:
                    batcher.question.create(
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
            except:
                await db.questionsbox.delete(
                    where={
                        "id": question_box.id
                    }
                )

        await message_sender(text="نه بابا، آزمونتو ساختی داپش", reply_markup=keyboard, edit=False)

        if for_admin:
            return AdminStates.SHOW_ADMIN_ACTIONS
        else:
            return HeadStates.HEAD_ACTION_DECIDER

    return add_question_box_action


async def show_users_list(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    should_ignore = await ignore_none_admin(update, ctx)
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
