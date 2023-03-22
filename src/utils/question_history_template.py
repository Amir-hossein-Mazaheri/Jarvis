from prisma.models import QuestionOption


def question_history_template(label: str, options: list[QuestionOption]):
    question = f"<b>{label}</b>\n\n"

    for option in options:
        question += f"{'✅' if option.is_answer else '❌'} {option.label}\n\n"

    question += "---------------------------------------------------------\n\n"

    return question
