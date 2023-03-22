def show_user(nickname: str, student_code: str, is_admin: bool, counter: int = None):
    user = ""

    if counter:
        user += f"#{counter} "

    user += f"{nickname} --- {student_code} --- {'Admin' if is_admin else 'Student'}\n\n"

    user += "---------------------------------------------------------------------------\n\n"

    return user
