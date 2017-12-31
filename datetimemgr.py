import datefinder
import datetime
import re

days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
short_days = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]


def get_datetime(string):
    # Pre-processing
    string = string.replace(".", ":")
    string = parse_dayofweek(string)

    m = re.search("(\d{1,2})[-/](\d{1,2})([-/]\d{1,4})?", string)
    now = datetime.datetime.now()

    # Handle the case when no year stated
    if m:
        tmp = m.group(0)
        day = m.group(1)
        month = months[int(m.group(2)) - 1]
        year = m.group(3) if m.group(3) else str(now.year)
        string = re.sub(tmp, day + " " + month + " " + year, string)
    try:
        dt = datefinder.find_dates(string).__next__()

        if dt.time().strftime("%H:%M") == "00:00":
            dt.replace(hour=23, minute=59, second=59)

        if dt < now:
            return dt.replace(year=now.year + 1)

        return dt
    except StopIteration:
        return string


def datetime2str(dt):
    if type(dt) is not datetime.datetime:
        return dt

    dayofweek, date, time = reformat(dt)

    if time == "23:59":
        return "{}, {}".format(dayofweek, date)

    return "{}, {}, {}".format(dayofweek, date, time)


def reformat(dt):
    return short_days[dt.date().weekday()].title(), "{} {} {}".format(dt.day,
                                                                      months[dt.month - 1],
                                                                      dt.year), \
           dt.time().strftime("%H:%M")


def parse_dayofweek(string):
    try:
        m = re.search("(mon)|(tue)|(wed)|(thu)|(fri)|(sat)|(sun)", string.lower())
        n = re.search("\d", string)

        if m and not n:
            string += " 23:59:59"  # Add a dummy time

        return string
    except AttributeError:
        return string


def is_datetime(dt_str):
    return type(get_datetime(dt_str)) is datetime.datetime
