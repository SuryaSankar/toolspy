from __future__ import absolute_import
from datetime import datetime, timedelta
import calendar
import time

def unix_time(dt):
    epoch = datetime.utcfromtimestamp(0)
    delta = dt - epoch
    return delta.total_seconds()


def unix_time_millis(dt):
    return int(unix_time(dt) * 1000)


def local_time_now(timedelta_mins_from_utc=None):
    if timedelta_mins_from_utc is None:
        timedelta_mins_from_utc = int(-time.timezone / 60)
    return datetime.utcnow() + timedelta(minutes=timedelta_mins_from_utc)


def ist_now():
    return local_time_now(timedelta_mins_from_utc=330)


def readable_date(dt):
    return "%s %s, %s" % (calendar.month_name[dt.month], dt.day, calendar.day_name[dt.weekday()])


def totimestamp(dt, epoch=datetime(1970, 1, 1)):
    td = dt - epoch
    # return td.total_seconds()
    return (
        td.microseconds + (
            td.seconds + td.days * 86400) * 10**6) / 10**6


def timedelta_mins(dt1, dt2):
    return int((dt1 - dt2).total_seconds()/60)


def daysdiff(d1, d2):
    return (d1-d2).days


def today(timedelta_mins_from_utc=None):
    return local_time_now(timedelta_mins_from_utc=None).date()


def n_days_ago(n, timedelta_mins_from_utc=None):
    return today(timedelta_mins_from_utc=timedelta_mins_from_utc) - timedelta(days=n)

def n_days_later(n, timedelta_mins_from_utc=None):
    return today(timedelta_mins_from_utc=timedelta_mins_from_utc) + timedelta(days=n)


def yesterday(timedelta_mins_from_utc=None):
    return n_days_ago(1, timedelta_mins_from_utc=timedelta_mins_from_utc)


def tomorrow(timedelta_mins_from_utc=None):
    return n_days_later(1, timedelta_mins_from_utc=timedelta_mins_from_utc)
