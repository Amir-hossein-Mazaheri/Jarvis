from prisma.enums import UserRole


def show_user(nickname: str, student_code: str, role: UserRole, counter: int = None, ignore_trailing_dashes=False):
    user = ""

    persian_role = ""

    if role == UserRole.ADMIN:
        persian_role = "ادمین"
    elif role == UserRole.HEAD:
        persian_role = "هد"
    else:
        persian_role = "استف"

    if counter:
        user += f"#{counter} "

    user += f"{nickname} --- {student_code} --- {persian_role}"

    if not ignore_trailing_dashes:
        user += "\n\n--------------------------------------------------------\n\n"

    return user
