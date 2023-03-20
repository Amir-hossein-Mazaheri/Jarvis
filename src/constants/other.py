from enum import Enum

STUDENT_CODE_LENGTH = 8

QUESTION_ID_KEY = "question_id"
NEXT_QUESTION_ID_KEY = "next_question_id"
CORRECT_QUESTIONS_KEY = "correct_questions_key"
WRONG_QUESTIONS_KEY = "wrong_questions_key"


class RegisterMode(Enum):
    EDIT = "EDIT"
    CREATE = "CREATE"
