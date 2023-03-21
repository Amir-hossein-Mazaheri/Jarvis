from telegram import Update, ReplyKeyboardMarkup


async def show_question(update: Update, question: str, options: list[str]):
    keyboard = ReplyKeyboardMarkup(
        list(map(lambda option: [option], options)), one_time_keyboard=True, input_field_placeholder="Pick one...")

    text = (
        "<b>Answer The Question</b>\n\n"
        f"{question}"
    )

    await update.message.reply_text(text=text, reply_markup=keyboard)
