#########################################################
# Add Generic methods independent of any App logic here.
# This module is meant to be a Python tool set.
#########################################################

from datetime import datetime, timedelta
from decimal import Decimal
import uuid
import os
# from werkzeug.utils import secure_filename
from functools import wraps
import errno
import signal
import csv
import MySQLdb
import requests
from contextlib import contextmanager


from code_inspection_tools import *
from web_tools import *
from collection_tools import *
from math_tools import *
from filesystem_tools import *
from datetime_tools import *
from csv_xl_tools import *


CUBIC_INCHES_IN_CUBIC_FEET = 12 * 12 * 12


class TimeoutError(Exception):
    pass


def timeout(seconds=10, error_message=os.strerror(errno.ETIME)):
    def decorator(func):
        def _handle_timeout(signum, frame):
            raise TimeoutError(error_message)

        def wrapper(*args, **kwargs):
            signal.signal(signal.SIGALRM, _handle_timeout)
            signal.alarm(seconds)
            try:
                result = func(*args, **kwargs)
            finally:
                signal.alarm(0)
            return result

        return wraps(func)(wrapper)

    return decorator


def boolify(val):
    if val is None:
        return False
    if isinstance(val, bool):
        return val
    return val.lower() in ['true', 'yes']


@contextmanager
def dbconn(server, user, password, database=None):
    if database is None:
        conn = MySQLdb.connect(server, user, password)
    else:
        conn = MySQLdb.connect(server, user, password, database)
    cursor = conn.cursor()
    yield cursor
    conn.close()


def get_if(obj, attr):
    return getattr(obj, attr) if obj else None


def join(words, delimiter=","):
    return delimiter.join([str(w)for w in words if w is not None])


def get_subclass(parent_class, discriminator):
    try:
        return next(mclass for mclass in all_subclasses(parent_class)
                    if mclass.__mapper_args__['polymorphic_identity'] == discriminator)
    except:
        return None


def int_safe_cast(val):
    if val is None:
        return None
    return int(val)


def null_safe_type_cast(_type_to_cast, val):
    if val is None:
        return None
    return _type_to_cast(val)


def fetch_nested_key(obj, key_string):
    if key_string is None:
        return None
    keys = key_string.split(".")
    curr_obj = obj
    for key in keys:
        if curr_obj is None:
            return None
        curr_obj = getattr(curr_obj, key)
    return curr_obj


def fetch_nested_key_from_dict(obj, key_string):
    if key_string is None:
        return None
    keys = key_string.split(".")
    curr_obj = obj
    for key in keys:
        if curr_obj is None:
            return None
        curr_obj = curr_obj.get(key)
    return curr_obj
