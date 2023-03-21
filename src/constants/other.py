from enum import Enum

STUDENT_CODE_LENGTH = 8

QUESTION_BOX_ID_KEY = "question_box_id_key"
QUESTION_ID_KEY = "question_id"
SEEN_QUESTIONS_KEY = "seen_questions"
NEXT_QUESTION_ID_KEY = "next_question_id"
TOTAL_QUESTIONS_KEY = "total_questions"
CORRECT_QUESTIONS_KEY = "correct_questions"
WRONG_QUESTIONS_KEY = "wrong_questions"


class RegisterMode(Enum):
    EDIT = "EDIT"
    CREATE = "CREATE"
