from datetime import datetime

from src.utils.db import db


async def get_next_question_id(prev_question_id: int):
    question = await db.question.find_first(order={
        'created_at': "desc"
    }, where={
        "deadline": {
            "gte": datetime.now()
        },
        "id": {
            "lt": prev_question_id
        }
    })

    if not bool(question):
        return None

    return question.id
