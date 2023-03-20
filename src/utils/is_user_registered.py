from src.utils.db import db


async def is_user_registered(user_id: int):
    user = await db.user.find_unique(
        where={
            'tel_id': user_id
        }
    )

    return bool(user)
