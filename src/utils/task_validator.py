from schema import Schema, And, Use


def task_validator(json):
    task_schema = Schema(
        [{
            "username": And(str, lambda s: bool(s.strip())),
            "tasks": [{
                "job": And(str, lambda s: bool(s.strip())),
                "weight": And(Use(float), float, lambda f: f > 0),
                "deadline": And(Use(int), int, lambda i: i > 0)
            }]
        }]
    )

    return task_schema.is_valid(json)
