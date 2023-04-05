from typing import TypeAlias, Literal
from telegram.ext import CallbackQueryHandler

from src.utils.exact_matcher import exact_matcher
from src.utils.SuperBaseHandler import SuperBaseHandler, CallbackT, GuardT

MatherT: TypeAlias = Literal["exact", "prefix"]


class SuperCallbackQueryHandler(CallbackQueryHandler, SuperBaseHandler):
    def prefix_matcher(self, data: str):
        def prefix_matcher_action(callback_data: str):
            return callback_data.split(" ")[0] == data

        return prefix_matcher_action

    def __init__(
            self,
            callback: CallbackT,
            matcher: str,
            matcher_type: MatherT = "exact",
            guard: GuardT = "registration"
    ) -> None:
        self._callback = callback
        self._guard = guard

        super().__init__(self._callback_wrapper, pattern=exact_matcher(matcher)
                         if matcher_type == "exact" else self.prefix_matcher(matcher))
