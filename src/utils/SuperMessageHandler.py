from telegram import Update
from telegram.ext import MessageHandler
from telegram.ext._utils.types import HandlerCallback, CCT, RT
from telegram.ext.filters import BaseFilter

from src.utils.SuperBaseHandler import SuperBaseHandler, GuardT


class SuperMessageHandler(MessageHandler, SuperBaseHandler):
    def __init__(
        self,
        filters: BaseFilter,
        callback: HandlerCallback[Update, CCT, RT],
        guard: GuardT = "registration"
    ):
        self._callback = callback
        self._guard = guard

        super().__init__(filters, self._callback_wrapper)
