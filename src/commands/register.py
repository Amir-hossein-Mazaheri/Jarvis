from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, ConversationHandler

from src.utils.db import db
from src.utils.is_user_registered import is_user_registered
from src.utils.get_back_to_menu_button import get_back_to_menu_button
from src.constants.other import STUDENT_CODE_LENGTH, RegisterMode, LAST_MESSAGE_KEY
from src.constants.states import RegisterStates, EditStates
from src.utils.get_actions_keyboard import get_actions_keyboard
from src.utils.is_user_registered import is_user_registered


async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    keyboard = await get_actions_keyboard(update, ctx)

    text = ""

    if await is_user_registered(user_id):
        text = "به ربات مدریت اعضای AICup خوش اومدی\n\n"
    else:
        text = (
            "به ربات مدریت اعضای AICup خوش اومدی\n\n"
            "برای استفاده از خدمات ربات باید <b>ثبت نام</b> کنی"
        )

    sent_message = await update.message.reply_text(text=text, reply_markup=keyboard)
    ctx.user_data[LAST_MESSAGE_KEY] = sent_message.id


async def ask_for_student_code(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    last_message = ctx.user_data.get(LAST_MESSAGE_KEY)

    if await is_user_registered(user_id):
        sent_message = await update.message.reply_text(text="شما قبلا ثبت نام کرده اید")
        ctx.user_data[LAST_MESSAGE_KEY] = sent_message.id

        return ConversationHandler.END

    keyboard = InlineKeyboardMarkup(
        [
            [get_back_to_menu_button("❌ " + "کنسل")]
        ]
    )

    sent_message = await ctx.bot.edit_message_text(message_id=last_message, chat_id=update.effective_chat.id, text="این مرحله برای استفاده از ربات لازمه، پس کد دانشجوییت رو برام بفرست", reply_markup=keyboard)
    ctx.user_data[LAST_MESSAGE_KEY] = sent_message.id

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

        if len(student_code) != STUDENT_CODE_LENGTH:
            sent_message = await update.message.reply_text(text="کد دانشجویی که فرستادی اشتباهه دوباره کد دانشجوییت رو بفرست")
            ctx.user_data[LAST_MESSAGE_KEY] = sent_message.id

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

        sent_message = await update.message.reply_text(text=reply_text, reply_markup=keyboard)
        ctx.user_data[LAST_MESSAGE_KEY] = sent_message.id

        if mode == RegisterMode.CREATE:
            return RegisterStates.REGISTER_NICKNAME
        else:
            return ConversationHandler.END

    return register_student_code_action


def register_nickname(mode: RegisterMode):
    async def register_nickname_action(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        nickname = update.message.text

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

        sent_message = await update.message.reply_text(text=reply_text, reply_markup=await get_actions_keyboard(update, ctx))
        ctx.user_data[LAST_MESSAGE_KEY] = sent_message.id

        return ConversationHandler.END

    return register_nickname_action
