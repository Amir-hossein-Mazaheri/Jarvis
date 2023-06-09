import os
import logging
from math import ceil
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, ConversationHandler
from datetime import datetime

from src.utils.db import db
from src.utils.question_history_template import question_history_template
from src.utils.get_actions_keyboard import get_actions_keyboard, KeyboardActions
from src.utils.get_back_to_menu_button import get_back_to_menu_button
from src.utils.send_message import send_message
from src.utils.get_user import get_user
from src.constants.commands import NEXT_QUESTIONS_PAGE, PREV_QUESTIONS_PAGE, START
from src.constants.other import LAST_QUESTIONS_PAGE_KEY


async def show_help(update: Update, ctx: ContextTypes.DEFAULT_TYPE, message_sender):
    bot_name = os.getenv("BOT_NAME")

    text = (
        f"به {bot_name} خوش اومدی 👋\n\n"
        "🤖 کارایی که میتونی با این ربات انجام بدی:\n\n"
        "   🟡 دیدن و ثبت تسک هایی که داری\n\n"
        "   🔴 جواب به آزمونی(آزمون هایی) که هد تیمت برات گذاشته\n\n"
        "   🔵 دیدن نتایج آزمون هایی که شرکت کردی\n\n"
        "   🟢 دیدن سوالای آزمون هایی که قبلا برگزار شده با جواباشون\n\n"
        "   🟣 ویرایش شماره دانشجویی یا اسمت توی ربات\n\n"
        "-----------------------------------------------------------------------------------"
    )

    await message_sender(text=text, reply_markup=await get_actions_keyboard(update, ctx))


async def questions_history(update: Update, ctx: ContextTypes.DEFAULT_TYPE, message_sender):
    user_id = update.effective_user.id
    user = await get_user(user_id)
    questions_per_page = os.getenv("QUESTIONS_PER_PAGE", 4)

    callback_query = update.callback_query
    page = ctx.user_data.get(LAST_QUESTIONS_PAGE_KEY)

    curr_page = int(page) if page else 1

    if callback_query:
        data = callback_query.data

        if data == NEXT_QUESTIONS_PAGE:
            curr_page += 1
        elif data == PREV_QUESTIONS_PAGE:
            curr_page -= 1

    where_options = {
        "question_box": {
            "deadline": {
                "lt": datetime.now()
            },
            "team": user.team
        }
    }

    questions = await db.question.find_many(
        where=where_options,
        take=questions_per_page,
        skip=(curr_page - 1) * questions_per_page,
        include={
            "options": True
        }
    )

    if len(questions) == 0:
        return await message_sender(text="فعلا سوالی نداریم", reply_markup=await get_actions_keyboard(update, ctx, [KeyboardActions.HISTORY]))

    questions_count = await db.question.count(where=where_options)

    total_pages = ceil(questions_count / questions_per_page)

    keyboard_buttons = []

    if curr_page < total_pages:
        keyboard_buttons.append(
            InlineKeyboardButton(
                "⏭️ " + "صفحه بعدی", callback_data=NEXT_QUESTIONS_PAGE)
        )

    if curr_page != 1:
        keyboard_buttons.append(
            InlineKeyboardButton(
                "صفحه قبل" + " ⏮️", callback_data=PREV_QUESTIONS_PAGE),
        )

    keyboard = InlineKeyboardMarkup(
        [keyboard_buttons, [get_back_to_menu_button()]]
    )

    questions_template = ""

    questions_template += f"صفحه فعلی <b>{curr_page}#</b>\n\n"

    for question in questions:
        questions_template += question_history_template(
            question.question, question.options)

    questions_template += f"صفحه فعلی <b>#{curr_page}</b>\n\n"

    ctx.user_data[LAST_QUESTIONS_PAGE_KEY] = curr_page

    if callback_query:
        await message_sender(text=questions_template, reply_markup=keyboard)
    else:
        await message_sender(text=questions_template, reply_markup=keyboard, edit=False)


async def back_to_menu(update: Update, ctx: ContextTypes.DEFAULT_TYPE, message_sender):
    await message_sender(text="🟥 " + "منوی ربات", reply_markup=await get_actions_keyboard(update, ctx))

    # to make sure that it exits conversation wether it get used in conversation handler
    return ConversationHandler.END


async def cleaner(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.delete()


async def error_handler(update: object, ctx: ContextTypes.DEFAULT_TYPE):
    logging.error(ctx.error)

    if isinstance(update, Update):
        message_sender = send_message(update, ctx)

        await message_sender(text=f"متاسفانه مشکلی پیش اومده، اگه با /{START} درست نشد بهمون پیام بده تا مشکل رو رفع کنم")
