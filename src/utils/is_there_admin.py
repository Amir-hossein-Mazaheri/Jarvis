from src.utils.db import db


async def is_there_admin():
    user = await db.user.find_first(
        where={
            'is_admin': True
        }
    )

    return bool(user)
