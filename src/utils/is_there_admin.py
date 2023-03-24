from prisma.enums import UserRole

from src.utils.db import db


async def is_there_admin():
    user = await db.user.find_first(
        where={
            'role': UserRole.ADMIN
        }
    )

    return bool(user)
