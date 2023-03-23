from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from prisma.models import QuestionOption

from src.constants.other import LAST_MESSAGE_KEY
from src.constants.commands import SKIP_QUESTIONS, QUIT_QUESTIONS


async def show_question(update: Update, ctx: ContextTypes.DEFAULT_TYPE, question: str, options: list[QuestionOption]):
    last_message = ctx.user_data.get(LAST_MESSAGE_KEY)

    keyboard_buttons = list(map(lambda option: [InlineKeyboardButton(
        option.label, callback_data=option.id)], options))

    keyboard_buttons.append([
        InlineKeyboardButton("⏭️ SKIP", callback_data=SKIP_QUESTIONS),
        InlineKeyboardButton("🔚 QUIT", callback_data=QUIT_QUESTIONS)
    ])

    keyboard = InlineKeyboardMarkup(
        keyboard_buttons
    )

    text = (
        "<b>Answer The Question</b>\n\n"
        f"{question}"
    )

    sent_message = await ctx.bot.edit_message_text(message_id=last_message, chat_id=update.effective_chat.id, text=text, reply_markup=keyboard)
    ctx.user_data[LAST_MESSAGE_KEY] = sent_message.id
