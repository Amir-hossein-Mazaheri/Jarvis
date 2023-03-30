from telegram import Update
from telegram.ext import ContextTypes
from prisma.enums import Team, UserRole
from prisma.models import User

from src.utils.db import db
from src.constants.commands import START


def send_notification(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    async def notification_sender(text: str, user_id: int = None, team: Team = None):
        user: User = None

        if user_id:
            user = await db.user.find_unique(
                where={
                    'tel_id': user_id
                }
            )
        else:
            user = await db.user.find_first(
                where={
                    'team': team,
                    'OR': [
                        {
                            'role': UserRole.ADMIN
                        },
                        {
                            'role': UserRole.HEAD
                        }
                    ]
                },
                order={
                    'created_at': 'asc'
                }
            )

        sent_message = await ctx.bot.send_message(chat_id=user.chat_id, text=text + f"\n\n برای دیدن دوباره منو روی /{START} کلیک کن")

        ctx.bot_data[user.id] = sent_message.id

    return notification_sender
