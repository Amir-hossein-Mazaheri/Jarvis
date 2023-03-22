from src.utils.db import db


async def is_admin(user_id: int):
    user = await db.user.find_first(
        where={
            'tel_id': user_id,
            'is_admin': True
        }
    )

    return bool(user)
