def show_user(nickname: str, student_code: str, is_admin: bool, counter: int = None):
    user = ""

    if counter:
        user += f"#{counter} "

    user += f"{nickname} --- {student_code} --- {'ادمین' if is_admin else 'دانشجو'}\n\n"

    user += "---------------------------------------------------------------------------\n\n"

    return user
