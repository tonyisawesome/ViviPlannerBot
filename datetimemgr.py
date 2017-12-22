import datefinder
import datetime
import re

days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def str2datetime(string):
    m = re.search("(\d{1,2})[-/.](\d{1,2})([-/.]\d{1,4})?", string)

    # Handle the case of no year stated
    if m:
        tmp = m.group(0)
        day = m.group(1)
        month = months[int(m.group(2)) - 1]

        if m.group(3) is None:
            string = re.sub(tmp, day + " " + month, string)

    try:
        return datefinder.find_dates(string).__next__()
    except StopIteration:
        return string


def datetime2str(dt):
    if type(dt) is not datetime.datetime:
        return dt

    dayofweek, date, time = reformat(dt)

    if time == "00:00":
        return "{}, {}".format(dayofweek, date)

    return "{}, {}, {}".format(dayofweek, date, time)


def reformat(dt):
    if dt.day < 13:
        month, day = dt.day, dt.month
    else:
        day, month = dt.day, dt.month

    return days[dt.date().weekday()], "{} {} {}".format(day, months[month - 1], dt.year), dt.time().strftime("%H:%M")
