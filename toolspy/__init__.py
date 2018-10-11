#########################################################
# Add Generic methods independent of any App logic here.
# This module is meant to be a Python tool set.
#########################################################

from itertools import chain, groupby, product
from operator import attrgetter, itemgetter
from contextlib import contextmanager
from inspect import ismethod
import re
from datetime import datetime, timedelta
from decimal import Decimal
import uuid
import os
# from werkzeug.utils import secure_filename
from functools import wraps
import errno
import signal
from collections import OrderedDict
import calendar
import xlsxwriter
from random import choice
import csv

# import MySQLdb
# from sqlalchemy.ext.associationproxy import (
#     _AssociationDict, _AssociationList)
# from sqlalchemy.orm.collections import (
#     InstrumentedList, MappedCollection)
try:
    from urllib import urlencode
    from urlparse import parse_qs, urlsplit, urlunsplit
except:
    pass

import requests


from code_inspection_tools import *
from web_tools import *
from ds_tools import *
from math_tools import *
from filesystem_tools import *



CUBIC_INCHES_IN_CUBIC_FEET = 12 * 12 * 12


# def is_list_like(rel_instance):
#     return (isinstance(rel_instance, list) or isinstance(
#         rel_instance, _AssociationList) or isinstance(
#         rel_instance, InstrumentedList))


# def is_dict_like(rel_instance):
#     return (isinstance(rel_instance, dict) or isinstance(
#         rel_instance, _AssociationDict) or isinstance(
#         rel_instance, MappedCollection))


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







# def generate_unique_file_name(seed_name):
#     return "%s_%s_%s" % (ist_now().strftime("%Y%m%d_%H%M%S%f"),
#                          uuid.uuid4().hex[0:6],
#                          secure_filename(seed_name))


# def save_with_unique_name(_file, location):
#     filename = generate_unique_file_name(_file.filename)
#     _file.save(os.path.join(location, filename))
#     return (filename, _file)


def boolify(val):
    if val is None:
        return False
    if isinstance(val, bool):
        return val
    return val.lower() in ['true', 'yes']



def get_if_exists(obj, attr):
    return getattr(obj, attr, None) if obj else None



def sanitize(source_dict, whitelist, additional_params={}, keys_to_modify={},
             value_filterer=lambda v: False,
             type_caster={}):
    # RIght now behavior is undefined if there is overlap between keys_to_modify
    # and type_caster
    """
    >>> raw={'name': 'surya', 'email': 'surya@s.com', 'bad_param': '<SCRIPT></SCRIPT>'}
    >>> raw={'name': 'surya', 'email': 'surya@s.com', 'bad_param': '<SCRIPT></SCRIPT>', 'postalcode': '55544'}
    >>> sanitize(raw, whitelist=['name', 'email', 'postalcode'], additional_params={'state': 'Wyoming', 'country': 'US'}, keys_to_modify={'postalcode':'zipcode'})
    {'email': 'surya@s.com', 'state': 'Wyoming', 'country': 'US', 'zipcode': '55544', 'name': 'surya'}
    """
    items = source_dict.items()
    for k, v in items:
        if k not in whitelist or value_filterer(v):
            del source_dict[k]
        elif k in keys_to_modify:
            source_dict[keys_to_modify[k]] = v
            del source_dict[k]
        if k in type_caster:
            if not isinstance(v, type_caster[k]):
                source_dict[k] = type_caster[k](v)

    return merge(source_dict, additional_params)



def capitalize_words(sentence):
    return ' '.join(word.capitalize() for word in sentence.split(" "))


def getattr_safe(obj, attr):
    attr = getattr(obj, attr)
    if ismethod(attr):
        return attr()
    return attr


def serialize_attrs(obj, *args):
    """
    >>> serialize_attrs(Customer.first(), 'id', 'email')
    {'id': 1L, 'email': u'mr.@howe.com'}
    """
    return dict((arg, getattr_safe(obj, arg)) for arg in args)


def grouplist(olist, key, strip_single_object_lists=False):
    """
    >>> customers
    [fulton@hills.com, maximus@collins.com, metta@nienow.com, mr.@howe.com, ruby@bogisich-watsica.biz]
    >>> customers[0].city="Delhi"
    >>> customers[1].city="Delhi"
    >>> customers[2].city="Mumbai"
    >>> customers[3].city="Mumbai"
    >>> customers[4].city="Chennai"
    >>> grouplist(customers, 'city')
    {'Chennai': [ruby@bogisich-watsica.biz],
     'Delhi': [fulton@hills.com, maximus@collins.com],
     'Mumbai': [metta@nienow.com, mr.@howe.com]}
    """
    result = {}
    for k, items in group(olist, key):
        items_list = list(items)
        if len(items_list) == 1 and strip_single_object_lists:
            result[k] = items_list[0]
        else:
            result[k] = items_list
    return result
    # return dict(
    #     (k, list(items))
    #     for k, items in group(olist, key))


def keygetter(key):
    return lambda x: x[key]


def group(olist, key):
    """
    Same functionality as grouplist. But returns iterator instead of list
    """
    olist = list(olist)
    if isinstance(olist[0], dict):
        getter_lambda = keygetter
    else:
        getter_lambda = attrgetter
    return groupby(sorted(
        olist, key=getter_lambda(key)), key=getter_lambda(key))


def deep_group(olist, keys, sort_attr=None, serializer=None,
               attr_to_show=None,
               serializer_args=[], serializer_kwargs={},
               strip_single_object_lists=False,
               preserve_order=False):
    """
    >>> customers[0].country="India"
    >>> customers[0].state="UP"
    >>> customers[0].city="Delhi"
    >>> customers[1].country="India"
    >>> customers[1].state="UP"
    >>> customers[1].city="Delhi"
    >>> customers[2].country="India"
    >>> customers[2].state="UP"
    >>> customers[2].city="Agra"
    >>> customers[3].country="India"
    >>> customers[3].state="TN"
    >>> customers[3].city="Chennai"
    >>> customers[4].country="China"
    >>> customers[4].state="Tibet"
    >>> customers[4].city="Lhasa"
    >>> deep_group(customers, keys=['country', 'state', 'city'])
    {'China': {'Tibet': {'Lhasa': [ruby@bogisich-watsica.biz]}},
     'India': {'TN': {'Chennai': [mr.@howe.com]},
               'UP': {'Delhi': [fulton@hills.com, maximus@collins.com],
               'Agra': [metta@nienow.com]}}}
    """
    if len(olist) == 0:
        return {}
    if len(keys) == 0:
        return olist
    if sort_attr:
        olist.sort(key=attrgetter(sort_attr))
    else:
        olist.sort(key=lambda o: tuple(getattr(o, k) for k in keys))
    result = {}
    for k, items in group(olist, keys[0]):
        items = list(items)
        if len(keys) == 1:
            if strip_single_object_lists and len(items) == 1:
                if serializer:
                    result[k] = getattr(
                        items[0], serializer)(*serializer_args,
                                              **serializer_kwargs)
                elif attr_to_show is not None:
                    result[k] = getattr(
                        items[0], attr_to_show)
                else:
                    result[k] = items[0]
            else:
                if serializer:
                    result[k] = [getattr(
                        item, serializer)(*serializer_args,
                                          **serializer_kwargs)
                        for item in items]
                elif attr_to_show is not None:
                    result[k] = [getattr(
                        item, attr_to_show) for item in items]
                else:
                    result[k] = items
        else:
            result[k] = deep_group(
                items, keys[1:],
                serializer=serializer,
                serializer_args=serializer_args,
                serializer_kwargs=serializer_kwargs,
                strip_single_object_lists=strip_single_object_lists,
                preserve_order=preserve_order,
                attr_to_show=attr_to_show)
    if preserve_order:
        result = OrderedDict(sorted(result.items()), key=lambda t: t[0])
    return result


def strip_bad_chars(string, chars=[' ', '_', ';', ',', '"', "'"]):
    for char in chars:
        string = string.replace(char, '')
    return string


def append_if_absent(l, i):
    if i not in l:
        l.append(i)
    return l


def add_to_list_in_dict(item, list_name, dictionary):
    append_if_absent(set_if_absent_and_get(dictionary, list_name, []), item)


@contextmanager
def use_and_throw(d, k):
    if k in d:
        yield getattr(d, k)
        del d.k


@contextmanager
def chdir(directory):
    cwd = os.getcwd()
    os.chdir(directory)
    yield
    os.chdir(cwd)


# @contextmanager
# def dbconn(server, user, password, database=None):
#     if database is None:
#         conn = MySQLdb.connect(server, user, password)
#     else:
#         conn = MySQLdb.connect(server, user, password, database)
#     cursor = conn.cursor()
#     yield cursor
#     conn.close()


def unix_time(dt):
    epoch = datetime.utcfromtimestamp(0)
    delta = dt - epoch
    return delta.total_seconds()


def unix_time_millis(dt):
    return int(unix_time(dt) * 1000)


def ist_now():
    return datetime.utcnow()+timedelta(minutes=330)


def public_dict(obj):
    d = dict((k, v) for k, v in obj.__dict__.iteritems()
             if not k.startswith('_'))
    return d


def pop_items(l):
    while len(l) > 0:
        yield l.pop()


def putdict(d, k, dv):
    if k not in d:
        d[k] = dv
    return d[k]


def is_not_none(d, k):
    return k in d and d[k] is not None


def set_if_absent_and_get(d, k, dv):
    if k not in d:
        setattr(d, k, dv)
    return getattr(d, k)


def get_if(obj, attr):
    return getattr(obj, attr) if obj else None


def join(words, delimiter=","):
    return delimiter.join([str(w)for w in words if w is not None])


def abbreviated_name(name, append_digit=None):
    """
    Returns a readable abbreviated name by removing vowels from the middle of
    the string and keeping the first and last letters of words.
    The final result is trimmed to 6 characters
    >>>abbreviated_name("I convert caffeine to code")
    'ICNVRT'
    """
    vowels = ['A', 'E', 'I', 'O', 'U']

    def words_of(name):
        return name.split()

    def strip_vowels(word):
        if len(word) > 2:
            return word[0]+filter(lambda l:
                                  l not in vowels, word[1:-1]) + word[-1]
        else:
            return word

    concatenate = ''.join

    abbr = concatenate([strip_vowels(word) for word in words_of(
        name.upper())])[0:6]

    if append_digit:
        abbr = abbr+str(append_digit)

    return abbr


def get_subdomain(host):
    """
    >>> get_subdomain('vendor.inkmonk.in')
    'vendor'
    >>> get_subdomain('vendor.us.inkmonk.com')
    'vendor.us'
    >>> get_subdomain('vendor.us')
    ''
    >>> get_subdomain('inkmonk.com')
    ''
    >>> get_subdomain('inkmonk')
    ''
    >>> get_subdomain('inkmonk.com')
    ''
    >>> get_subdomain('us.inkmonk.com')
    'us'
    """

    host_parts = host.split('.')
    subs = host_parts[:-2]
    return '.'.join(subs)


def get_subclass(parent_class, discriminator):
    try:
        return next(mclass for mclass in all_subclasses(parent_class)
                    if mclass.__mapper_args__['polymorphic_identity'] == discriminator)
    except:
        return None


def readable_date(dt):
    return "%s %s, %s" % (calendar.month_name[dt.month], dt.day, calendar.day_name[dt.weekday()])


def all_combinations(list_of_keys, lists_of_lists_of_vals):
    return [dict(zip(list_of_keys, combo)) for combo in product(
        *lists_of_lists_of_vals)]


def add_to_struct(key, item, struct):
    append_if_absent(set_if_absent_and_get(struct, key, []), item)


def write_xlsx_sheet(xlsx_file, rows=[], cols=[]):
    """
    If cols is mentioned, then each entry in rows should be of format
    {
        "Name": "Surya", "Email": "Surya@inkmonk.com"
    }
    If cols is not given, then each entry in row should be a list of values
    ["Surya", "Surya@inkmonk.com"]
    """
    workbook = xlsxwriter.Workbook(xlsx_file)
    worksheet = workbook.add_worksheet()
    bold = workbook.add_format({'bold': 1})
    text_wrap = workbook.add_format({'text_wrap': 1})
    if len(cols) > 0:
        for col, heading in enumerate(cols):
            worksheet.write(0, col, heading, bold)
        for row_index, row in enumerate(rows):
            for col_index, col_name in enumerate(cols):
                worksheet.write(
                    row_index + 1, col_index, row.get(col_name, ""), text_wrap)
    else:
        for row_index, row_cells in enumerate(rows):
            for col, cell in enumerate(row_cells):
                worksheet.write(row_index, col, cell, text_wrap)
    workbook.close()


def is_subset_of(set1, set2):
    return all(el in set2 for el in set1)

def int_safe_cast(val):
    if val is None:
        return None
    return int(val)

def null_safe_type_cast(_type_to_cast, val):
    if val is None:
        return None
    return _type_to_cast(val)

def delete_dict_keys(d, keys):
    for k in keys:
        if k in d:
            del d[k]

def copy_without_keys(d, keys):
    output = {}
    for k in d.keys():
        if k not in keys:
            output[k] = d[k]
    return output
    # for k in keys:
    #     if k in d:
    #         del d[k]

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

def sum_attr_vals(items, prop, skip_nones=False):
    total = 0
    for item in items:
        val = getattr(item, prop)
        if val is None:
            if skip_nones:
                val = 0
            else:
                return None
        total += val
    return total


def totimestamp(dt, epoch=datetime(1970, 1, 1)):
    td = dt - epoch
    # return td.total_seconds()
    return (
        td.microseconds + (
            td.seconds + td.days * 86400) * 10**6) / 10**6


def join_non_nulls(strings, delimiter=", "):
    return delimiter.join([s for s in strings if s is not None and s != ""])


def split_csv_into_columns(csvfilepath):
    cols = {}
    with open(csvfilepath) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            for k, v in row.items():
                if k not in cols:
                    cols[k] = []
                cols[k].append(v)
    return cols



def median(items, sort=True):
    if sort:
        items = sorted(items, key=itemgetter(0))
    freq_sum = sum(item[1] for item in items)
    partial_freq_sum = 0
    for item in items:
        partial_freq_sum += item[1]
        if partial_freq_sum * 2 >= freq_sum:
            return item[0]
    return None

def sans_none(*items):
    skipped = [i for i in items if i is not None]
    return skipped

def min_sans_none(*items):
    skipped = sans_none(*items)
    if len(skipped) == 0:
        return None
    return min(skipped)






