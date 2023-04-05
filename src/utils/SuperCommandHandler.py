from telegram import Update
from telegram.ext import CommandHandler
from telegram.ext._utils.types import CCT, RT, HandlerCallback
from telegram._utils.types import SCT

from src.utils.SuperBaseHandler import SuperBaseHandler, GuardT


class SuperCommandHandler(CommandHandler, SuperBaseHandler):
    def __init__(
            self,
            command: SCT[str],
            callback: HandlerCallback[Update, CCT, RT],
            guard: GuardT = "registration"
    ):
        self._callback = callback
        self._guard = guard

        super().__init__(command, self._callback_wrapper)
