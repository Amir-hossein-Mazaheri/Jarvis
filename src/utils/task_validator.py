from schema import Schema, And, Use, Or


def task_validator(json):
    tasks_schema = [{
        "job": And(str, lambda s: bool(s.strip())),
        "weight": And(Use(float), float, lambda f: f > 0),
        "deadline": And(Use(int), int, lambda i: i > 0)
    }]

    task_schema = Schema(
        Or(
            [
                {
                    "username": And(str, lambda s: bool(s.strip())),
                    "tasks": tasks_schema
                }
            ],
            {
                "tasks": tasks_schema
            }
        ),
        ignore_extra_keys=True
    )

    task_schema.validate(json)

    return task_schema.is_valid(json)
