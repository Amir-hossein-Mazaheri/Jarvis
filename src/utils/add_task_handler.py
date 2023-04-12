from prisma.enums import Team, UserRole

from src.utils.db import db
from src.utils.create_tasks import create_tasks


async def add_task_handler(parsed_file, team: Team):
    async with db.batch_() as batcher:
        if type(parsed_file) == dict:
            users = await db.user.find_many(
                where={
                    "OR": [
                        {
                            "team": team
                        },
                        {
                            "secondary_teams": {
                                "has": team
                            }
                        }
                    ],
                    "NOT": {
                        "OR": [
                            {
                                "role": UserRole.ADMIN
                            },
                            {
                                "role": UserRole.ADMIN
                            }
                        ]
                    }
                }
            )

            for user in users:
                create_tasks(user.id, team, parsed_file["tasks"], batcher)

            return

        for user_info in parsed_file:
            user = await db.user.find_first(
                where={
                    "name": {
                        "mode": "insensitive",
                        "equals": "@" + user_info["username"].lstrip("@")
                    },
                    "OR": [
                        {
                            "team": team
                        },
                        {
                            "secondary_teams": {
                                "has": team
                            }
                        }
                    ]
                }
            )

            if not bool(user):
                continue

            create_tasks(user.id, team, user_info["tasks"], batcher)
