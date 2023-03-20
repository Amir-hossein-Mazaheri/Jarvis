from enum import Enum

STUDENT_CODE_LENGTH = 8

QUESTION_ID_KEY = "question_id"
NEXT_QUESTION_ID_KEY = "next_question_id"
TOTAL_QUESTIONS_KEY = "total_questions"
CORRECT_QUESTIONS_KEY = "correct_questions"
WRONG_QUESTIONS_KEY = "wrong_questions"


class RegisterMode(Enum):
    EDIT = "EDIT"
    CREATE = "CREATE"
