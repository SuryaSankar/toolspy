from datetime import datetime, timedelta
import calendar


def unix_time(dt):
    epoch = datetime.utcfromtimestamp(0)
    delta = dt - epoch
    return delta.total_seconds()


def unix_time_millis(dt):
    return int(unix_time(dt) * 1000)


def ist_now():
    return datetime.utcnow() + timedelta(minutes=330)


def readable_date(dt):
    return "%s %s, %s" % (calendar.month_name[dt.month], dt.day, calendar.day_name[dt.weekday()])


def totimestamp(dt, epoch=datetime(1970, 1, 1)):
    td = dt - epoch
    # return td.total_seconds()
    return (
        td.microseconds + (
            td.seconds + td.days * 86400) * 10**6) / 10**6
