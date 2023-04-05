from typing import Literal, TypeAlias
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from telegram.ext._utils.types import HandlerCallback, CCT, RT

from src.utils.ignore_none_head import ignore_none_head
from src.utils.ignore_none_admin import ignore_none_admin
from src.utils.ignore_none_registered import ignore_none_registered
from src.utils.send_message import send_message

GuardT: TypeAlias = Literal["none", "registration", "head", "admin"]
CallbackT = HandlerCallback[Update, CCT, RT]


class SuperBaseHandler:
    _guard: GuardT = None
    _callback: CallbackT = None

    async def _callback_wrapper(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        should_ignore = None

        match self._guard:
            case "registration":
                should_ignore = await ignore_none_registered(update, ctx)
            case "head":
                should_ignore = await ignore_none_head(update, ctx)
            case "admin":
                should_ignore = await ignore_none_admin(update, ctx)

        if should_ignore:
            return ConversationHandler.END

        message_sender = send_message(update, ctx)

        return await self._callback(update, ctx, message_sender)
