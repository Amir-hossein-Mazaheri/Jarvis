from src.utils.db import db


async def get_next_question_id(question_box_id: int, prev_question_id: int, seen_questions: list[int]):
    """give you the next question id based on the questions user have seen

    Args:
        question_box_id (int): id of current question box
        prev_question_id (int): previous question id
        seen_questions (list[int]): list of questions that user have seen

    Returns:
        _type_: int
    """
    question = await db.question.find_first(
        where={
            'question_box_id': question_box_id,
            "id": {
                'not_in': seen_questions
            }
        },
        order={
            'created_at': 'desc'
        }
    )

    if not bool(question):
        return None

    return question.id
