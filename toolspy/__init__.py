#########################################################
# Add Generic methods independent of any App logic here.
# This module is meant to be a Python tool set.
#########################################################

from itertools import chain, groupby, product
from operator import attrgetter
from contextlib import contextmanager
from inspect import ismethod
import re
from datetime import datetime, timedelta
from decimal import Decimal
import uuid
import os
# from werkzeug.utils import secure_filename
import math
from functools import wraps
import errno
import signal
from collections import OrderedDict
import calendar
import xlsxwriter

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

EMAIL_REGEX = re.compile(r"[^@]+@[^@]+\.[^@]+")

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


def scd(cls):
    if len(cls.__subclasses__())==0:
        return {}
    return {x: scd(x) for x in cls.__subclasses__()}

# Lifted from http://stackoverflow.com/a/12897375
def set_query_params(url, params):
    """Given a URL, set or replace a query parameter and return the
    modified URL.

    >>> set_query_parameter('http://example.com?foo=bar&biz=baz', 'foo', 'stuff')
    'http://example.com?foo=stuff&biz=baz'

    """
    scheme, netloc, path, query_string, fragment = urlsplit(url)
    query_params = parse_qs(query_string)
    for param_name, param_value in params.items():
        query_params[param_name] = [param_value]
    new_query_string = urlencode(query_params, doseq=True)

    return urlunsplit((scheme, netloc, path, new_query_string, fragment))


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


def all_subclasses(cls):
    return cls.__subclasses__() + [
        g for s in cls.__subclasses__() for g in all_subclasses(s)]


def hypotenuse(x, y):
    return math.sqrt(x**2 + y**2)


def mean(list):
    if len(list) == 0:
        return None
    try:
        return round_float(sum(x or 0 for x in list)/len(list))
    except:
        return None


def union(list_of_lists):
    if len(list_of_lists) == 0:
        return []
    return list(set.union(*[set(l) for l in list_of_lists]))
    # return frozenset().union(*[set(l) for l in list_of_lists])


def intersection(list_of_lists):
    if len(list_of_lists) == 0:
        return []
    return list(set.intersection(*[set(l) for l in list_of_lists]))


def difference(list1, list2):
    result = []
    for item in list1:
        if item not in list2:
            result.append(item)
    return result
    # return list(set(list1).difference(set(list2)))


def symmetric_difference(list1, list2):
    return list(set(list1).symmetric_difference(set(list2)))


def round_float(value, precision=2):
    return math.ceil(value*(10**precision))/(10**precision)


def dict_map(d, mapper):
    return {k: mapper(v) for k, v in d.iteritems()}


def random_string(length=None):
    string1 = str(uuid.uuid4()).replace('-', '')
    string2 = str(uuid.uuid4()).replace('-', '')
    if length:
        string = string1[:length/2] + string2[:(length-length/2)]
    return string


def npartition(string, n=1, delimiter=' '):
    """
    Similar to python's built in partition method. But will
    split at the nth occurence of delimiter
    """
    groups = string.split(delimiter)
    return (delimiter.join(groups[:n]), delimiter, delimiter.join(groups[n:]))


def percentage(numerator, denominator):
    value = float(numerator)*100/float(denominator)
    return math.ceil(value*100)/100


def percentage_markup(original, percent):
    return monetize(original + (Decimal(percent) / 100) * original)

def discount_percent(original_price, new_price):
    return percentage(original_price-new_price, original_price)


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


def unique_sublists(lst, duplicate_checker=None):
    if duplicate_checker is None:
        duplicate_checker = lambda item, lst: item in lst
    sublists = [[]]
    for item in lst:
        for sublist in sublists:
            if not duplicate_checker(item, sublist):
                sublist.append(item)
                break
        else:
            sublists.append([item])

    return sublists


def is_email(mailstr):
    """
    Checks if a string matches the Email regex
    """
    return ((isinstance(mailstr, str) or isinstance(mailstr, unicode))
            and bool(EMAIL_REGEX.match(mailstr)))


def place_nulls(key, input_keyvals, output_results):
    """
    Useful in a specific case when you want to verify that a mapped list
    object returns objects corresponding to input list.
    Hypothetical example:
    Customer.raw_get_all([1,2,3]) returns [C1, C3]
    There is no customer with id 2 in db. But this is bad for us becaause
    we will want to iterate like zip (input, output) if possible. So we
    need to place nulls wherever the list is missing an output value. This
    function will make the list as [C1, None, C3]
    """
    if len(input_keyvals) != len(output_results):
        for index, keyval in enumerate(input_keyvals):
            try:
                if getattr(output_results[index], key) != keyval:
                    output_results.insert(index, None)
            except IndexError:
                output_results.insert(index, None)
    return output_results


def reverse_dict(d):
    return {v: k for k, v in d.items()}


def subdict(dictionary, keys):
    """
    >>>a={1:3, 4:5, 6:7}
    >>>subdict(a, [4,6])
    {4: 5, 6: 7}
    """
    return (dict((k, dictionary[k]) for k in keys if k in dictionary)
            if len(keys) > 0 else dictionary)


def remove_and_mark_duplicate_dicts(list_of_dicts, keys):
    result_dicts = []
    marks = {}
    for idx, d in enumerate(list_of_dicts):
        for rd in result_dicts:
            if subdict(d, keys) == subdict(rd, keys):
                marks[idx] = result_dicts.index(rd)
                break
        else:
            result_dicts.append(d)
    return (result_dicts, marks)


def dict_without_keys(dictionary, keys):
    return {k: v for k, v in dictionary.items() if k not in keys}


def add_kv_to_dict(dictionary, key, value):
    """
    >>> a={1:3, 4:5, 6:7}
    >>> add_kv_to_dict(a, 6, 9)
    {1: 3, 4: 5, 6: 9}
    """
    return dict(chain(dictionary.items(), [(key, value)]))


def merge(*dicts):
    """
    >>> a={1:2, 3:4}
    >>> b={5:6, 7:8}
    >>> merge(a,b)
    {1: 2, 3: 4, 5: 6, 7: 8}
    """
    return dict(chain(*[_dict.iteritems() for _dict in dicts]))


def add_kv_if_absent(dictionary, key, value):
        if key not in dictionary:
            dictionary[key] = value
        return dictionary


def has_duplicates(l):
    try:
        return len(l) != len(set(l))
    except:
        for i in range(len(l)):
            for j in range(i + 1, len(l)):
                if l[i] == l[j]:
                    return True
        return False


def remove_duplicates(l):
    return list(set(l))


def get_if_exists(obj, attr):
    return getattr(obj, attr, None) if obj else None


def monetize(number):
    """
    Function used for rounding off numbers to a fixed number of
    places.
    >>> monetize(3.4389)
    Decimal('3.44')
    >>> monetize(3.4334)
    Decimal('3.43')
    """
    if number is None:
        return None
    return Decimal(number).quantize(Decimal('.01'))


def quantize(number):
    if number is None:
        return None
    return Decimal(number).quantize(Decimal('.01'))


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


def is_int(s):
    if isinstance(s, int):
        return True
    else:
        try:
            int(s)
            return True
        except:
            return False


def flatten(list_of_lists):
    """
    >>> flatten([[1,2], [3,4,5]])
    [1, 2, 3, 4, 5]
    """
    return [item for sublist in list_of_lists for item in sublist]


def filtered_list(olist, exclude_list):
    return filter(lambda i: i not in exclude_list, olist)


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


def correct_subclass(klass, discriminator):
    try:
        return next(
            c for c in all_subclasses(klass)
            if c.__mapper_args__['polymorphic_identity'] == discriminator)
    except:
        return None

def is_subset_of(set1, set2):
    return all(el in set2 for el in set1)

def int_safe_cast(val):
    if val is None:
        return None
    return int(val)
