from src.utils.db import db


async def get_user(user_id: int):
    return await db.user.find_unique(
        where={
            "tel_id": user_id
        }
    )
