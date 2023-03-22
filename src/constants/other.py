from enum import Enum

STUDENT_CODE_LENGTH = 8
QUESTIONS_PER_PAGE = 4

QUESTION_BOX_ID_KEY = "question_box_id_key"
QUESTION_ID_KEY = "question_id"
SEEN_QUESTIONS_KEY = "seen_questions"
NEXT_QUESTION_ID_KEY = "next_question_id"
TOTAL_QUESTIONS_KEY = "total_questions"
CORRECT_QUESTIONS_KEY = "correct_questions"
WRONG_QUESTIONS_KEY = "wrong_questions"
LAST_USER_STAT_MESSAGE_KEY = "last_user_stat_message_key"
LAST_USER_QUESTION_BOX_STAT_KEY = "last_user_question_box_stat"
LAST_QUESTIONS_PAGE_KEY = "last_questions_page"
LAST_QUESTIONS_MESSAGE_KEY = "last_questions_message"


class RegisterMode(Enum):
    EDIT = "EDIT"
    CREATE = "CREATE"
