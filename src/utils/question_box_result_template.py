def question_box_result_template(c_answers: int | None, w_answers: int | None, t_answers: int, prefix: str = None):
    return (
        f"{prefix if prefix else ''}"
        "📃 نتیجه آزمون: \n\n"
        f"🟢 <b>تعداد جوابای درست</b>: {c_answers if c_answers != None else 0} \n"
        f"🔴 تعداد جوابای غلط: {w_answers if w_answers != None else 0} \n"
        f"⭕ تعداد سوالات بی جواب: {t_answers} \n\n"
        "هر نتیجه ای که هست عالیه 👏"
    )
