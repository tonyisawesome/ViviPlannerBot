import datefinder
import datetime
import re

days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def str2datetime(string):
    # Pre-processing
    string = string.replace(".", ":")
    string = parse_dayofweek(string)

    m = re.search("(\d{1,2})[-/](\d{1,2})([-/]\d{1,4})?", string)

    # Handle the case when no year stated
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


short_days = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]


def parse_dayofweek(string):
    try:
        m = re.search("(mon)|(tue)|(wed)|(thu)|(fri)|(sat)|(sun)", string.lower())
        n = re.search("\d", string)

        if m and not n:
            string += " 00:00"  # Add a dummy time

        return string
    except AttributeError:
        return string
