import os
from math import ceil
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
from src.utils.get_users_keyboard import get_users_keyboard
from src.utils.is_admin import is_admin
from src.utils.question_box_validator import question_box_validator
from src.utils.toggle_enable_to_edit import toggle_enable_to_edit
from src.utils.get_enable_to_edit import get_enable_to_edit
from src.utils.send_notification import send_notification
from src.constants.commands import REGISTER_ADMIN
from src.constants.states import AdminStates, HeadStates
from src.constants.commands import ADMIN_SHOW_USERS_LIST, BACK_TO_ADMIN_ACTIONS,\
    ADMIN_PROMPT_ADD_QUESTION_BOX, ADMIN_SHOW_USERS_LIST_BUTTONS,\
    BACK_TO_HEAD_ACTIONS, ADMIN_SHOW_QUESTIONS_BOX_TO_REMOVE, \
    ADMIN_SHOW_QUESTION_BOXES_FOR_STAT, ADMIN_SHOW_HEADS_LIST_TO_REMOVE, REMOVE_HEAD_PREFIX, \
    ADMIN_SHOW_NONE_HEAD_LIST_TO_REMOVE, ADMIN_TOGGLE_EDIT_INFO, ADMIN_PUBLIC_ANNOUNCEMENT,\
    ADMIN_PUBLIC_VERSION_CHANGE_ANNOUNCEMENT, ADMIN_NEXT_USERS_PAGE_PREFIX,\
    ADMIN_PREV_USERS_PAGE_PREFIX, ADMIN_ANNOUNCE_END_OF_BOT_UPDATE


async def show_admin_actions(update: Update, ctx: ContextTypes.DEFAULT_TYPE, message_sender):
    should_ignore = await ignore_none_registered(update, ctx)
    is_there_any_admin = await is_there_admin()
    is_user_admin = await is_admin(update, ctx)
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
            [InlineKeyboardButton("❌🧑‍💼 " + "عزل هد",
                                  callback_data=ADMIN_SHOW_HEADS_LIST_TO_REMOVE),
             InlineKeyboardButton("🧑‍💼 " + "افزودن هد",
                                  callback_data=ADMIN_SHOW_USERS_LIST_BUTTONS)
             ],
            [InlineKeyboardButton("❌👤 " + "حذف کاربر",
                                  callback_data=ADMIN_SHOW_NONE_HEAD_LIST_TO_REMOVE),
             InlineKeyboardButton("📃 " + "نمایش لیست کاربران",
                                  callback_data=ADMIN_SHOW_USERS_LIST)
             ],
            [InlineKeyboardButton("⚔️" + "غیر فعال سازی قابلیت تغییر اطلاعات" if await get_enable_to_edit() else "✅ " +
                                  "فعال سازی قابلیت ویرایش اطلاعات", callback_data=ADMIN_TOGGLE_EDIT_INFO)],
            [InlineKeyboardButton("📢 " + "اعلان عمومی",
                                  callback_data=ADMIN_PUBLIC_ANNOUNCEMENT)],
            [InlineKeyboardButton("❌🆕 " + "اعلان اتمام آپدیت ربات", callback_data=ADMIN_ANNOUNCE_END_OF_BOT_UPDATE), InlineKeyboardButton(
                "🆕 " + "اعلان آپدیت ربات", callback_data=ADMIN_PUBLIC_VERSION_CHANGE_ANNOUNCEMENT),
             ],
            [get_back_to_menu_button()]
        ]
    )

    await message_sender(text="🧑‍💼 " + "لیست کارای ادمینی", reply_markup=keyboard)

    return AdminStates.ADMIN_ACTIONS


async def register_admin(update: Update, ctx: ContextTypes.DEFAULT_TYPE, message_sender):
    should_ignore = await ignore_none_registered(update, ctx)
    is_there_any_admin = await is_there_admin()

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
    async def add_question_box_action(update: Update, ctx: ContextTypes.DEFAULT_TYPE, message_sender):
        user_id = update.effective_user.id
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


async def show_users_list(update: Update, ctx: ContextTypes.DEFAULT_TYPE, message_sender):
    parsed_callback_query = update.callback_query.data.split(" ")
    users_per_page = os.getenv("USERS_PER_PAGE", 20)

    curr_page = int(parsed_callback_query[1]) if len(
        parsed_callback_query) == 2 else 1

    where_options = {
        "NOT": {
            "role": UserRole.ADMIN
        }
    }

    users = await db.user.find_many(
        where=where_options,
        take=users_per_page,
        skip=(curr_page - 1) * users_per_page
    )

    users_count = await db.user.count(where=where_options)

    keyboard_buttons = [
        [
            InlineKeyboardButton(
                "بازگشت به لیست کارای ادمینی", callback_data=BACK_TO_ADMIN_ACTIONS),
            get_back_to_menu_button()
        ]
    ]

    if len(users) == 0:
        await message_sender(text="کاربری وجود نداره دیگه", reply_markup=InlineKeyboardMarkup(keyboard_buttons))
        return AdminStates.ADMIN_ACTIONS

    total_pages = ceil(users_count / users_per_page)

    if curr_page < total_pages:
        keyboard_buttons = [[InlineKeyboardButton(
            "⏭️" + "صفحه بعدی",
            callback_data=f"{ADMIN_NEXT_USERS_PAGE_PREFIX} {curr_page + 1}"
        )]] + keyboard_buttons

    if curr_page != 1:
        keyboard_buttons = [[InlineKeyboardButton(
            "صفحه قبلی" + "⏮️",
            callback_data=f"{ADMIN_PREV_USERS_PAGE_PREFIX} {curr_page - 1}"
        )]] + keyboard_buttons

    users_template = ""

    for i, user in enumerate(users):
        users_template += show_user(user.name, user.nickname, user.student_code,
                                    user.role, i + 1)

    await message_sender(text=users_template, reply_markup=InlineKeyboardMarkup(keyboard_buttons))

    return AdminStates.ADMIN_ACTIONS


def show_users_list_buttons(prefix: str, action: str):
    async def show_users_list_buttons_actions(update: Update, ctx: ContextTypes.DEFAULT_TYPE, message_sender):
        await message_sender(text=f"کدوم کاربر رو میخوای {action} کنی؟", reply_markup=await get_users_keyboard(exclude_heads=True, prefix=prefix))

        return AdminStates.ADMIN_ACTIONS

    return show_users_list_buttons_actions


async def add_head(update: Update, ctx: ContextTypes.DEFAULT_TYPE, message_sender):
    user_id = int(update.callback_query.data.split(" ")[1])

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


async def show_heads_list_to_remove(update: Update, ctx: ContextTypes.DEFAULT_TYPE, message_sender):
    users = await db.user.find_many(
        where={
            "role": UserRole.HEAD,
        },
        order={
            "created_at": "desc"
        }
    )

    keyboard = InlineKeyboardMarkup(
        [*list(map(
            lambda user: [
                InlineKeyboardButton(
                    text=f"{user.student_code} -- {user.nickname} -- {user.team.replace('_', ' ')}", callback_data=f"{REMOVE_HEAD_PREFIX} {user.id}")
            ], users)),
         [
            InlineKeyboardButton(
                "بازگشت به لیست کارای ادمینی", callback_data=BACK_TO_ADMIN_ACTIONS),
            get_back_to_menu_button()
        ]]
    )

    await message_sender(text="لیست هد هایی که میتونی عزل کنی", reply_markup=keyboard)

    return AdminStates.ADMIN_ACTIONS


async def remove_head(update: Update, ctx: ContextTypes.DEFAULT_TYPE, message_sender):
    head_id = int(update.callback_query.data.split(" ")[1])

    await db.user.update(
        where={
            "id": head_id
        },
        data={
            "role": UserRole.STUDENT
        }
    )

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("بازگشت به لیست عزل هد",
                              callback_data=ADMIN_SHOW_HEADS_LIST_TO_REMOVE)],
        [
            InlineKeyboardButton(
                "بازگشت به لیست کارای ادمینی", callback_data=BACK_TO_ADMIN_ACTIONS),
            get_back_to_menu_button()
        ]

    ])

    await message_sender(text="این یارو رو عزل کردی 😞", reply_markup=keyboard)

    return AdminStates.ADMIN_ACTIONS


async def remove_user(update: Update, ctx: ContextTypes.DEFAULT_TYPE, message_sender):
    user_id = int(update.callback_query.data.split(" ")[1])

    await db.user.delete(
        where={
            "id": user_id
        }
    )

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("بازگشت به لیست حذف کاربر",
                              callback_data=ADMIN_SHOW_NONE_HEAD_LIST_TO_REMOVE)],
        [
            InlineKeyboardButton(
                "بازگشت به لیست کارای ادمینی", callback_data=BACK_TO_ADMIN_ACTIONS),
            get_back_to_menu_button()
        ]

    ])

    await message_sender(text="کاربر بدبخت رو حذفش کردی 🫠", reply_markup=keyboard)

    return AdminStates.ADMIN_ACTIONS


async def toggle_edit_info(update: Update, ctx: ContextTypes.DEFAULT_TYPE, message_sender):
    await toggle_enable_to_edit()

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "بازگشت به لیست کارای ادمینی", callback_data=BACK_TO_ADMIN_ACTIONS),
            get_back_to_menu_button()
        ]

    ])

    await message_sender(text="قابلیت تغییر اطلاعات همه تغییر کرد", reply_markup=keyboard)

    return AdminStates.ADMIN_ACTIONS


async def public_announcer(text: str, update: Update, ctx: ContextTypes.DEFAULT_TYPE, message_sender):
    notification_sender = send_notification(update, ctx)

    users = await db.user.find_many(
        where={
            "NOT": {
                "role": UserRole.ADMIN
            }
        }
    )

    for user in users:
        await notification_sender(text=text, user_id=user.tel_id)


async def public_announcement(update: Update, ctx: ContextTypes.DEFAULT_TYPE, message_sender):
    should_prompt = update.callback_query

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "بازگشت به لیست کارای ادمینی", callback_data=BACK_TO_ADMIN_ACTIONS),
            get_back_to_menu_button()
        ]

    ])

    if should_prompt:
        await message_sender(text="چیزی که می خوای به اعلان کنی رو بهم بگو", reply_markup=keyboard)

        return AdminStates.PUBLIC_ANNOUNCEMENT

    announcement_message = update.message.text

    sent_message = await message_sender(text="در حال ارسال اعلان های عمومی، لطفا منتظر بمون و کار دیگه هم نکن...", edit=False)

    await public_announcer(announcement_message, update, ctx, message_sender)

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "بازگشت به لیست کارای ادمینی", callback_data=BACK_TO_ADMIN_ACTIONS),
            get_back_to_menu_button()
        ]

    ])

    # for some unknown reason message_sender is not updating the correct message
    await ctx.bot.edit_message_text(
        chat_id=update.effective_chat.id,
        message_id=sent_message.id,
        text="اعلان عمومی ربات با موفقیت انجام شدش، داپش",
        reply_markup=keyboard
    )

    return AdminStates.ADMIN_ACTIONS


async def public_announcement_about_version_change(update: Update, ctx: ContextTypes.DEFAULT_TYPE, message_sender):
    should_prompt = update.callback_query

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "بازگشت به لیست کارای ادمینی", callback_data=BACK_TO_ADMIN_ACTIONS),
            get_back_to_menu_button()
        ]

    ])

    if should_prompt:
        await message_sender(text="چند ساعت دیگه ربات آپدیت میشه؟", reply_markup=keyboard)

        return AdminStates.PUBLIC_VERSION_CHANGE_ANNOUNCEMENT

    hours_left_to_bot_update = update.message.text

    sent_message = await message_sender(text="در حال ارسال اعلان های آپدیت ربات، لطفا منتظر بمون و کار دیگه هم نکن...", edit=False)

    await public_announcer(f"رفیق ربات {hours_left_to_bot_update} ساعت دیگر آپدیت میشه و به محض تموم شدن آپدیت همینجوری بهت میگیم", update, ctx, message_sender)

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "بازگشت به لیست کارای ادمینی", callback_data=BACK_TO_ADMIN_ACTIONS),
            get_back_to_menu_button()
        ]

    ])

    # for some unknown reason message_sender is not updating the correct message
    await ctx.bot.edit_message_text(
        chat_id=update.effective_chat.id,
        message_id=sent_message.id,
        text="اعلان آپدیت ربات با موفقیت انجام شدش، داپش",
        reply_markup=keyboard
    )

    return AdminStates.ADMIN_ACTIONS


async def announce_end_of_bot_update(update: Update, ctx: ContextTypes.DEFAULT_TYPE, message_sender):
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "بازگشت به لیست کارای ادمینی", callback_data=BACK_TO_ADMIN_ACTIONS),
            get_back_to_menu_button()
        ]

    ])

    await message_sender(text="در حال ارسال اعلان های آپدیت ربات، لطفا منتظر بمون و کار دیگه هم نکن...")

    await public_announcer(f"ربات با موفقیت آپدیت شد، <b>اگه بعد آپدیت منویی برات باز نمیشه میتونی بات رو clear history کنی</b>", update, ctx, message_sender)

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "بازگشت به لیست کارای ادمینی", callback_data=BACK_TO_ADMIN_ACTIONS),
            get_back_to_menu_button()
        ]

    ])

    await message_sender(text="اعلان اتمام آپدیت ربات با موفقیت ارسال شد", reply_markup=keyboard)

    return AdminStates.ADMIN_ACTIONS
