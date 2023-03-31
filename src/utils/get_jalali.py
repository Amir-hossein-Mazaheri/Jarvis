from datetime import datetime
from persiantools.jdatetime import JalaliDateTime


def get_jalali(datetime: datetime):
    date = datetime.fromtimestamp(datetime.timestamp())

    return JalaliDateTime(date).strftime(
        "%Y / %m / %d - %H:%M", locale="fa_IR")
