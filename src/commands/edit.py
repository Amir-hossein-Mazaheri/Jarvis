from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, ConversationHandler

from src.constants.states import EditStates
from src.utils.ignore_user import ignore_user
from src.utils.get_back_to_menu_button import get_back_to_menu_button
from src.constants.other import LAST_MESSAGE_KEY
from src.utils.get_actions_keyboard import get_actions_keyboard

EDIT_ACTIONS = {
    "student_code": "🧑‍💻 " + "شماره دانشجویی",
    "nickname": "📛 " + "اسم مستعار"
}


async def ask_to_edit_what(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    should_ignore = await ignore_user(update, ctx)
    last_message = ctx.user_data.get(LAST_MESSAGE_KEY)

    if should_ignore:
        return ConversationHandler.END

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(EDIT_ACTIONS["student_code"],
                              callback_data=EDIT_ACTIONS["student_code"])],
        [InlineKeyboardButton(EDIT_ACTIONS["nickname"],
                              callback_data=EDIT_ACTIONS["nickname"])],
        [get_back_to_menu_button()]
    ])

    sent_message = await ctx.bot.edit_message_text(message_id=last_message, chat_id=update.effective_chat.id, text="چیزی که میخوای عوض کنی رو انتخاب کن", reply_markup=keyboard)
    ctx.user_data[LAST_MESSAGE_KEY] = sent_message.id

    return EditStates.EDIT_DECIDER


async def edit_decider(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    action = update.callback_query.data
    last_message = ctx.user_data.get(LAST_MESSAGE_KEY)

    if action == EDIT_ACTIONS["nickname"]:
        sent_message = await ctx.bot.edit_message_text(message_id=last_message, chat_id=update.effective_chat.id, text="حالا اسم مستعار جدیدت رو بگو بهم")
        ctx.user_data[LAST_MESSAGE_KEY] = sent_message.id

        return EditStates.EDIT_NICKNAME
    elif action == EDIT_ACTIONS["student_code"]:
        sent_message = await ctx.bot.edit_message_text(message_id=last_message, chat_id=update.effective_chat.id, text="حالا شماره دانشجویی جدیدت رو بهم بگو")
        ctx.user_data[LAST_MESSAGE_KEY] = sent_message.id

        return EditStates.EDIT_STUDENT_CODE

    sent_message = await ctx.bot.edit_message_text(message_id=last_message, chat_id=update.effective_chat.id, text="عملیات نادرست")
    ctx.user_data[LAST_MESSAGE_KEY] = sent_message.id

    return EditStates.ASK_TO_EDIT_WHAT
