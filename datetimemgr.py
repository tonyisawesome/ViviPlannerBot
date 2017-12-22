import datefinder
from datetime import datetime


def str2datetime(string):
    matches = datefinder.find_dates(string)

    if not matches:
        return string

    dates = []

    for match in matches:
        dayofweek, date, time = reformat(match)
        dates.append("{}, {}, {}".format(dayofweek, date, match.time().strftime("%H:%M")))

    return dates[0]     # Assuming there is only one datetime for now


days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct❤ber", "Nov", "Dec"]


def reformat(dt):
    if dt.day < 13:
        month, day = dt.day, dt.month
    else:
        day, month = dt.day, dt.month

    return days[dt.date().weekday()], "{} {} {}".format(day, months[month - 1], dt.year), dt.time().strftime("%H:%M")
