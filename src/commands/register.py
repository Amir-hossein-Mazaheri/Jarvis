import os
import re
from telegram import Update, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from prisma.enums import Team, UserRole

from src.utils.db import db
from src.utils.is_user_registered import is_user_registered
from src.utils.get_back_to_menu_button import get_back_to_menu_button
from src.utils.get_actions_keyboard import get_actions_keyboard
from src.utils.is_user_registered import is_user_registered
from src.utils.get_teams_keyboard import get_teams_keyboard
from src.utils.get_user import get_user
from src.utils.get_enable_to_edit import get_enable_to_edit
from src.constants.other import STUDENT_CODE_LENGTH, RegisterMode
from src.constants.states import RegisterStates, EditStates
from src.constants.commands import REGISTER_TEAM_PREFIX


async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE, message_sender):
    bot_name = os.getenv("BOT_NAME")
    keyboard = await get_actions_keyboard(update, ctx)

    ctx._application.drop_chat_data(update.effective_chat.id)

    text = ""

    if await is_user_registered(update, ctx):
        text = f"به {bot_name} خوش اومدی 👋\n\n"
    else:
        text = (
            "به ربات مدریت اعضای AICup خوش اومدی\n\n"
            "برای استفاده از خدمات ربات باید <b>ثبت نام</b> کنی"
        )

    await message_sender(text=text, reply_markup=keyboard, edit=False)


async def ask_for_student_code(update: Update, ctx: ContextTypes.DEFAULT_TYPE, message_sender):
    if await is_user_registered(update, ctx):
        await message_sender(text="شما قبلا ثبت نام کرده اید")
        return ConversationHandler.END

    keyboard = InlineKeyboardMarkup(
        [
            [get_back_to_menu_button("❌ " + "کنسل")]
        ]
    )

    await message_sender(text="این مرحله برای استفاده از ربات لازمه، پس کد دانشجوییت رو برام بفرست", reply_markup=keyboard)

    return RegisterStates.REGISTER_STUDENT_CODE


def register_student_code(mode: RegisterMode):
    """
        This function return a bot handler function because it has to act
        for two purpose, editing and creating student code but the reply text and action
        after that differ, for that issue I made the parent function to take an arg
    """

    async def register_student_code_action(update: Update, ctx: ContextTypes.DEFAULT_TYPE, message_sender):
        user_id = update.effective_user.id
        chat_id = update.effective_chat.id
        name = update.effective_user.name
        student_code = update.message.text

        await update.message.delete()

        if mode == RegisterMode.EDIT:
            can_edit = await get_enable_to_edit()
            user = await get_user(user_id)

            if not can_edit and user.role != UserRole.ADMIN:
                await message_sender(text="متاسفانه قابلیت ویرایش قفل شده است", reply_markup=await get_actions_keyboard(update, ctx))
                return ConversationHandler.END

        if not re.match("^[0-9]*$", student_code):
            keyboard = InlineKeyboardMarkup(
                [
                    [get_back_to_menu_button()]
                ]
            )

            await message_sender(text="کد دانشجویی که فرستادی اشتباهه دوباره کد دانشجوییت رو بفرست", reply_markup=keyboard)

            if mode == RegisterMode.CREATE:
                return RegisterStates.REGISTER_STUDENT_CODE
            else:
                return EditStates.EDIT_STUDENT_CODE

        await db.user.upsert(
            where={
                "tel_id": user_id,
            },
            data={
                "create": {
                    "tel_id": user_id,
                    "student_code": student_code,
                    "name": name,
                    "nickname": name,
                    "chat_id": chat_id
                },
                "update": {
                    "student_code": student_code
                }
            }
        )

        reply_text = ""
        keyboard = None

        if mode == RegisterMode.CREATE:
            reply_text = "حالا تیمی که توشی رو انتخاب کن، این مرحله رو با دقت انجام بده"
            keyboard = get_teams_keyboard(REGISTER_TEAM_PREFIX)
        else:
            reply_text = "عالیه، شماره دانشجوییت تغییر کرد"
            keyboard = await get_actions_keyboard(update, ctx)

        await message_sender(text=reply_text, reply_markup=keyboard)

        if mode == RegisterMode.CREATE:
            return RegisterStates.REGISTER_TEAM
        else:
            return ConversationHandler.END

    return register_student_code_action


def register_team(mode: RegisterMode):
    async def register_team_action(update: Update, ctx: ContextTypes.DEFAULT_TYPE, message_sender):
        user_id = update.effective_user.id
        callback_team = update.callback_query.data.split(" ")[1]
        user = await get_user(user_id)

        if user.role == UserRole.HEAD:
            await message_sender(text="متاسفانه امکان تعویض تیم برای هد نیست", reply_markup=await get_actions_keyboard(update, ctx))

            return ConversationHandler.END

        if mode == RegisterMode.EDIT:
            can_edit = await get_enable_to_edit()

            if not can_edit and user.role != UserRole.ADMIN:
                await message_sender(text="متاسفانه قابلیت ویرایش قفل شده است", reply_markup=await get_actions_keyboard(update, ctx))
                return ConversationHandler.END

        selected_team = None

        for team in Team:
            if callback_team == team.value:
                selected_team = team.value
                break

        if not selected_team:
            await message_sender(text="تیمی که انتخاب کردی وجود ندارد دوباره انتخاب کن", reply_markup=get_teams_keyboard())
            return RegisterStates.REGISTER_TEAM

        await db.user.update(
            where={
                "tel_id": user_id
            },
            data={
                "team": selected_team
            }
        )

        keyboard = None
        reply_text = ""

        if mode == RegisterMode.CREATE:
            reply_text = "حالا اسمتم بهم بگو"
            keyboard = InlineKeyboardMarkup(
                [
                    [get_back_to_menu_button("❌ " + "کنسل")]
                ]
            )
        else:
            reply_text = "عالیه، تیمیت تغییر کرد"
            keyboard = await get_actions_keyboard(update, ctx)

        await message_sender(text=reply_text, reply_markup=keyboard)

        if mode == RegisterMode.CREATE:
            return RegisterStates.REGISTER_NICKNAME
        else:
            return ConversationHandler.END

    return register_team_action


def register_nickname(mode: RegisterMode):
    async def register_nickname_action(update: Update, ctx: ContextTypes.DEFAULT_TYPE, message_sender):
        user_id = update.effective_user.id
        nickname = update.message.text

        await update.message.delete()

        await db.user.update(
            where={
                "tel_id": user_id
            },
            data={
                "nickname": nickname
            }
        )

        reply_text = ""

        if mode == RegisterMode.CREATE:
            reply_text = "خب، ثبت نامت تموم شد حالا میتونی از امکانات ربات استفاده کنی"
        else:
            reply_text = "عالیه، اسمت تغییر کرد"

        await message_sender(text=reply_text, reply_markup=await get_actions_keyboard(update, ctx))

        return ConversationHandler.END

    return register_nickname_action
