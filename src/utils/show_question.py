from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from prisma.models import QuestionOption

from src.utils.send_message import send_message
from src.constants.commands import SKIP_QUESTIONS, QUIT_QUESTIONS, ANSWER_VALIDATOR_PREFIX


async def show_question(update: Update, ctx: ContextTypes.DEFAULT_TYPE, question: str, options: list[QuestionOption]):
    message_sender = send_message(update, ctx)

    keyboard_buttons = list(map(lambda option: [InlineKeyboardButton(
        option.label, callback_data=f"{ANSWER_VALIDATOR_PREFIX} {option.id}")], options))

    keyboard_buttons.append([
        InlineKeyboardButton("⏭️ رد کردن سوال", callback_data=SKIP_QUESTIONS),
        InlineKeyboardButton("🔚 اتمام آزمون", callback_data=QUIT_QUESTIONS)
    ])

    keyboard = InlineKeyboardMarkup(
        keyboard_buttons
    )

    text = (
        "❓ <b>سوالو جواب بده</b>\n\n"
        f"{question}"
    )

    await message_sender(text=text, reply_markup=keyboard)
