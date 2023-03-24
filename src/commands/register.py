from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, ConversationHandler

from src.utils.db import db
from src.utils.is_user_registered import is_user_registered
from src.utils.get_back_to_menu_button import get_back_to_menu_button
from src.utils.get_actions_keyboard import get_actions_keyboard
from src.utils.is_user_registered import is_user_registered
from src.utils.send_message import send_message
from src.constants.other import STUDENT_CODE_LENGTH, RegisterMode, IS_USER_REGISTERED
from src.constants.states import RegisterStates, EditStates


async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    keyboard = await get_actions_keyboard(update, ctx)
    message_sender = send_message(update, ctx)

    text = ""

    if await is_user_registered(update, ctx):
        text = "به ربات مدریت اعضای AICup خوش اومدی\n\n"
    else:
        text = (
            "به ربات مدریت اعضای AICup خوش اومدی\n\n"
            "برای استفاده از خدمات ربات باید <b>ثبت نام</b> کنی"
        )

    await message_sender(text=text, reply_markup=keyboard, edit=False)


async def ask_for_student_code(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    message_sender = send_message(update, ctx)

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

    async def register_student_code_action(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        name = update.effective_user.name
        student_code = update.message.text
        message_sender = send_message(update, ctx)

        await update.message.delete()

        if len(student_code) != STUDENT_CODE_LENGTH:
            await message_sender(text="کد دانشجویی که فرستادی اشتباهه دوباره کد دانشجوییت رو بفرست")

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
                },
                "update": {
                    "student_code": student_code
                }
            }
        )
        # ctx.user_data[IS_USER_REGISTERED] = "1"

        reply_text = ""
        keyboard = None

        if mode == RegisterMode.CREATE:
            reply_text = "حالا اسم مستعاری که می خوای داشته باشی رو هم برام بفرست (اگه نمی خوای کنسل رو بزن)"
            keyboard = InlineKeyboardMarkup(
                [
                    [get_back_to_menu_button("❌ " + "کنسل")]
                ]
            )
        else:
            reply_text = "عالیه، شماره دانشجوییت تغییر کرد"
            keyboard = await get_actions_keyboard(update, ctx)

        await message_sender(text=reply_text, reply_markup=keyboard)

        if mode == RegisterMode.CREATE:
            return RegisterStates.REGISTER_NICKNAME
        else:
            return ConversationHandler.END

    return register_student_code_action


def register_nickname(mode: RegisterMode):
    async def register_nickname_action(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        message_sender = send_message(update, ctx)
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
            reply_text = "عالیه، اسم مستعارت تغییر کرد"

        await message_sender(text=reply_text, reply_markup=await get_actions_keyboard(update, ctx))

        return ConversationHandler.END

    return register_nickname_action
