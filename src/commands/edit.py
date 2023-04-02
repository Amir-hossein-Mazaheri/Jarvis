from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, ConversationHandler

from src.utils.ignore_none_registered import ignore_none_registered
from src.utils.get_back_to_menu_button import get_back_to_menu_button
from src.utils.get_teams_keyboard import get_teams_keyboard
from src.utils.send_message import send_message
from src.constants.states import EditStates
from src.constants.commands import EDIT_TEAM_PREFIX

EDIT_ACTIONS = {
    "student_code": "🧑‍💻 " + "شماره دانشجویی",
    "nickname": "📛 " + "اسم",
    "team": "🧑‍🤝‍🧑 " + "تیم"
}


async def ask_to_edit_what(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    should_ignore = await ignore_none_registered(update, ctx)
    message_sender = send_message(update, ctx)

    if should_ignore:
        return ConversationHandler.END

    keyboard_buttons = []

    for key in EDIT_ACTIONS:
        keyboard_buttons.append([InlineKeyboardButton(
            EDIT_ACTIONS[key], callback_data=EDIT_ACTIONS[key])])

    keyboard_buttons.append([get_back_to_menu_button()])

    keyboard = InlineKeyboardMarkup(keyboard_buttons)

    await message_sender(text="چیزی که میخوای عوض کنی رو انتخاب کن", reply_markup=keyboard)

    return EditStates.EDIT_DECIDER


async def edit_decider(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    action = update.callback_query.data
    message_sender = send_message(update, ctx)

    keyboard = InlineKeyboardMarkup(
        [[get_back_to_menu_button()]]
    )

    if action == EDIT_ACTIONS["nickname"]:
        await message_sender(text="حالا اسم جدیدت رو بگو بهم", reply_markup=keyboard)
        return EditStates.EDIT_NICKNAME
    elif action == EDIT_ACTIONS["student_code"]:
        await message_sender(text="حالا شماره دانشجویی جدیدت رو بهم بگو", reply_markup=keyboard)
        return EditStates.EDIT_STUDENT_CODE
    elif action == EDIT_ACTIONS["team"]:
        await message_sender(text="تیمی که رفتی توش رو انتخاب کن", reply_markup=get_teams_keyboard(EDIT_TEAM_PREFIX))
        return EditStates.EDIT_TEAM

    await message_sender(text="عملیات نادرست")

    return EditStates.ASK_TO_EDIT_WHAT
