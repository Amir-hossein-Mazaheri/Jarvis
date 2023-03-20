from telegram import Update, ReplyKeyboardRemove
from telegram.ext import ConversationHandler


async def show_questions_result(update: Update, c_answer: int | None, w_answers: int | None):
    await update.message.reply_text(text="Nice you reached the end, good job.", reply_markup=ReplyKeyboardRemove())

    results = (
        "📃 Here is the result of what you did today: \n\n"
        f"🟢 <b>Correct Answers</b>: {c_answer if c_answer != None else 0} \n"
        f"🔴 Wrong Answers: {w_answers if w_answers != None else 0} \n\n"
        "you did a great job 👏"
    )

    await update.message.reply_text(text=results)

    return ConversationHandler.END
