from os import getcwd, getenv
from os.path import join
from typing import Union
from fastapi import FastAPI, Request
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from prisma.enums import UserRole

from src.utils.db import db

app = FastAPI()

app.add_middleware(GZipMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_methods=["*"],
    allow_headers=["*"]
)


@app.middleware('http')
async def connect_to_db(request: Request, call_next):
    if not db.is_connected():
        await db.connect()

    return await call_next(request)


@app.get("/teams/{head_tel_id}")
async def get_team_users(head_tel_id: int, q: Union[str, None] = None):
    head = await db.user.find_first(
        where={
            "tel_id": head_tel_id,
            "OR": [
                {
                    "role": UserRole.ADMIN
                },
                {
                    "role": UserRole.HEAD
                }
            ]
        }
    )

    if not bool(head):
        return []

    users = await db.user.find_many(
        where={
            "OR": [
                {
                    "team": head.team
                },
                {
                    "secondary_teams": {
                        "has": head.team
                    }
                }
            ],
            "NOT": {
                "OR": [
                    {
                        "role": UserRole.ADMIN
                    },
                    {
                        "role": UserRole.HEAD
                    }
                ]
            }
        }
    )

    return (list(map(lambda u: {"id": u.id, "username": u.name,  "nickname": u.nickname, "student_code": u.student_code}, users)))


app.mount('/', StaticFiles(directory=join(getcwd(),
          "webapp", "dist"), html=True), name='static')
