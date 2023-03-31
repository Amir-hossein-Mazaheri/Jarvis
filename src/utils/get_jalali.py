from datetime import datetime
from persiantools.jdatetime import JalaliDateTime


def get_jalali(datetime: datetime):
    date = datetime.fromtimestamp(datetime.timestamp())

    return JalaliDateTime(date).strftime(
        "%H:%M - %Y/%m/%d ", locale="fa_IR")
