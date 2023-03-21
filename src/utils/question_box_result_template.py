def question_box_result_template(c_answers: int | None, w_answers: int | None, t_answers: int):
    return (
        "📃 Here is the result of what you did today: \n\n"
        f"🟢 <b>Correct Answers</b>: {c_answers if c_answers != None else 0} \n"
        f"🔴 Wrong Answers: {w_answers if w_answers != None else 0} \n"
        f"⭕ Empty Answers: {t_answers} \n\n"
        "you did a great job 👏"
    )
