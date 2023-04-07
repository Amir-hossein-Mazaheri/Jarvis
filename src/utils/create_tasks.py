from datetime import timedelta, datetime
from prisma.enums import Team
from prisma import Batch


def create_tasks(user_id: int, team: Team, tasks: list, batcher: Batch):
    for task in tasks:
        deadline = datetime.now() + \
            timedelta(days=int(task["deadline"]))

        batcher.task.create(
            data={
                "job": task["job"],
                "weight": task["weight"],
                "deadline": deadline,
                "team": team,

                "user": {
                    "connect": {
                        "id": user_id
                    }
                }
            }
        )
