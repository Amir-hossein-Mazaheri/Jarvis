from schema import Schema, And, Optional


def question_box_validator(json):
    schema = Schema({
        "label": And(str, lambda s: bool(s.strip())),
        "deadline": And(int, lambda i: i > 0),
        "duration": And(int, lambda i: i > 0),
        Optional("team"): And(str, lambda s: bool(s.strip())),
        "questions": [
            {
                "label": And(str, lambda s: bool(s.strip())),
                "score": And(int, lambda i: i > 0),
                "options": [
                    {
                        "label": And(str, lambda s: bool(s.strip())),
                        "is_answer": bool
                    }
                ]
            }
        ]
    })

    return schema.is_valid(json)