# -*- coding: utf-8 -*-

"""Top-level package for Toolspy."""

from __future__ import absolute_import
import six
__author__ = """Surya Sankar"""
__email__ = 'suryashankar.m@gmail.com'
__version__ = '0.2.29'


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
import requests
from contextlib import contextmanager


from .code_inspection_tools import *
from .web_tools import *
from .collection_tools import *
from .math_tools import *
from .filesystem_tools import *
from .datetime_tools import *
from .csv_xl_tools import *
from .string_tools import *

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
    import MySQLdb
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

def get_attr_with_collection_handling(obj, attr):
    if isinstance(obj, list):
        return [get_attr_with_collection_handling(i, attr) for i in obj]
    elif isinstance(obj, dict):
        return {k: get_attr_with_collection_handling(v, attr) for k, v in six.iteritems(obj)}
    return getattr(obj, attr)

def smart_get(obj, key_string):
    if obj is None or key_string is None:
        return None
    if '.' not in key_string:
        return get_attr_with_collection_handling(obj, key_string)
    next_key, dot, remaining_keys = key_string.partition(".")
    next_obj = get_attr_with_collection_handling(obj, next_key)
    return smart_get(next_obj, remaining_keys)



def fetch_nested_key(obj, key_string):
    if key_string is None:
        return None
    keys = key_string.split(".")
    curr_obj = obj
    for key in keys:
        if curr_obj is None:
            return None
        if isinstance(curr_obj, dict):
            curr_obj = curr_obj.get(key)
        else:
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
