from __future__ import absolute_import
from collections import defaultdict
from itertools import chain, groupby, product
from operator import attrgetter, itemgetter
from collections import OrderedDict
from inspect import ismethod
from .math_tools import round_float
from contextlib import contextmanager
import six
from six.moves import range
from six.moves import zip


def get_if_exists(obj, attr):
    return getattr(obj, attr, None) if obj else None


def keygetter(key):
    return lambda x: x[key]


@contextmanager
def use_and_throw(d, k):
    if k in d:
        yield getattr(d, k)
        del d.k


def public_dict(obj):
    d = dict((k, v) for k, v in six.iteritems(obj.__dict__)
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


def mean(list):
    if len(list) == 0:
        return None
    try:
        return round_float(sum(x or 0 for x in list)/len(list))
    except:
        return None


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
    return {v: k for k, v in list(d.items())}


def subdict(dictionary, keys):
    """
    >>>a={1:3, 4:5, 6:7}
    >>>subdict(a, [4,6])
    {4: 5, 6: 7}
    """
    return (dict((k, dictionary[k]) for k in keys if k in dictionary)
            if len(keys) > 0 else dictionary)

# def copy_partial_dict(dictionary, keys_to_retain=None, keys_to_remove=None):
#     """
#     >>>a={1:3, 4:5, 6:7}
#     >>>subdict(a, [4,6])
#     {4: 5, 6: 7}
#     """
#     result = {}
#     if keys_to_retain:
#         for k in keys_to_retain:
#             if "." in k:
#                 prefix, dot, suffix = k.partition(".")
#                 if prefix in dictionary:
#                     if isinstance(dictionary[prefix], dict):

#             else:
#                 if k in dictionary:
#                     result[k] = dictionary[k]
#     return (dict((k, dictionary[k]) for k in keys if k in dictionary)
#             if len(keys) > 0 else dictionary)


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
    return {k: v for k, v in list(dictionary.items()) if k not in keys}


def add_kv_to_dict(dictionary, key, value):
    """
    >>> a={1:3, 4:5, 6:7}
    >>> add_kv_to_dict(a, 6, 9)
    {1: 3, 4: 5, 6: 9}
    """
    return dict(chain(list(dictionary.items()), [(key, value)]))


def merge(*dicts):
    """
    >>> a={1:2, 3:4}
    >>> b={5:6, 7:8}
    >>> merge(a,b)
    {1: 2, 3: 4, 5: 6, 7: 8}
    """
    return dict(chain(*[six.iteritems(_dict) for _dict in dicts]))

def deep_merge(*dicts):
    merged_dict = {}
    for _dict in dicts:
        for k, v in _dict.items():
            if k in merged_dict and isinstance(v, dict):
                merged_dict[k] = deep_merge(v, merged_dict[k])
            else:
                merged_dict[k] = v
    return merged_dict


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


def get_list_item(l, idx):
    if l is None or idx is None:
        return None
    if idx > len(l) - 1:
        return None
    return l[idx]


def insert_list_item(l, idx, item):
    if l is None or idx is None:
        return None
    if idx > len(l) - 1:
        for _ in range(idx):
            l.append(None)
        l.append(item)
    else:
        if l[idx] is None:
            l[idx] = item
        else:
            l.insert(idx, item)
    return l


def preceding_items_list(l, item):
    if item not in l:
        return []
    return l[:l.index(item)]


def succeeding_items_list(l, item):
    if item not in l:
        return []
    return l[l.index(item) + 1:]


def partition_list(l, pivot_item):
    return [preceding_items_list(l, pivot_item), pivot_item, succeeding_items_list(l, pivot_item)]


def merge_lists(list_of_lists):
    item_predecessors = {}
    unique_items = []
    for l in list_of_lists:
        for item in l:
            if item not in unique_items:
                unique_items.append(item)

    item_priorities = {}

    for item in reversed(unique_items):
        preceding_items = remove_duplicates(
            flatten([preceding_items_list(l, item) for l in list_of_lists]))
        for p_item in preceding_items:
            if p_item in item_predecessors and item in item_predecessors[p_item]:
                preceding_items.remove(p_item)
        item_predecessors[item] = preceding_items

    items_to_be_checked = difference(unique_items, list(item_priorities.keys()))
    loop_ctr = -1
    while len(items_to_be_checked) > 0 and loop_ctr <= 1000:
        loop_ctr += 1
        # print "Starting loop {0}".format(loop_ctr)
        # print "items to be checked ", items_to_be_checked
        for item in items_to_be_checked:
            # print "Item being checked is %s" % item
            predecessors = item_predecessors[item]
            # print "predecessors are ", predecessors
            if len(predecessors) == 0:
                item_priorities[item] = 0
                # print "Set priority of item to 0"
            else:
                if all(pred in item_priorities for pred in predecessors):
                    item_priorities[item] = max(
                        [item_priorities[p] for p in predecessors]) + 1
                    # print "Set priority of item to %s" % item_priorities[item]
        items_to_be_checked = difference(unique_items, list(item_priorities.keys()))
        # print "items to be checked at end of loop ", items_to_be_checked
        # print

    final_list = sorted(
        unique_items, key=lambda item: item_priorities.get(item) or 0)
    return final_list

# def merge_lists_in_same_order(list_of_lists):
#     final_list = []
#     successors = defaultdict(list)

#     for lst in list_of_lists:
#         for idx, item in enumerate(lst):
#             for successor in lst[idx+1:]:
#                 if successor not in successors[item]:
#                     successors[item].append(successor)
#                 if successor in successors:
#                     for secondary_successor in successors[successor]:

#     print successors
#     ranks = defaultdict(list)
#     for k, v in successors.items():
#         ranks[len(v)].append(k)
#     print ranks
#     return (successors, ranks)


def unique_sublists(lst, duplicate_checker=None):
    if duplicate_checker is None:
        def duplicate_checker(item, lst): return item in lst
    sublists = [[]]
    for item in lst:
        for sublist in sublists:
            if not duplicate_checker(item, sublist):
                sublist.append(item)
                break
        else:
            sublists.append([item])

    return sublists


def dict_map(d, mapper):
    return {k: mapper(v) for k, v in six.iteritems(d)}


def flatten(list_of_lists):
    """
    >>> flatten([[1,2], [3,4,5]])
    [1, 2, 3, 4, 5]
    """
    return [item for sublist in list_of_lists for item in sublist]


def filtered_list(olist, exclude_list):
    return [i for i in olist if i not in exclude_list]


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


def sans_none(*items):
    skipped = [i for i in items if i is not None]
    return skipped


def min_sans_none(*items):
    skipped = sans_none(*items)
    if len(skipped) == 0:
        return None
    return min(skipped)


def delete_dict_keys(d, keys):
    for k in keys:
        if k in d:
            del d[k]
        else:
            if '.' in k:
                prefix, dot, suffix = k.partition(".")
                if prefix in d:
                    if isinstance(d[prefix], dict):
                        delete_dict_keys(d[prefix], [suffix])
                    elif isinstance(d[prefix], list):
                        for dct in d[prefix]:
                            delete_dict_keys(dct, [suffix])
    return d


def copy_without_keys(d, keys):
    output = {}
    for k in d.keys():
        if k not in keys:
            output[k] = d[k]
    return output


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
    items = list(source_dict.items())
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


def transform_dict(
        d, keys_to_retain=None, keys_to_rename=None,
        skip_none_vals=True):
    result = {}
    for k, v in d.items():
        if v is None and skip_none_vals:
            continue
        if keys_to_retain is None or k in keys_to_retain:
            if keys_to_rename and k in keys_to_rename:
                key = keys_to_rename.get(k)
            else:
                key = k
            result[key] = v
    return result



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
    if len(olist) > 0:
        for k, items in group(olist, key):
            items_list = list(items)
            if len(items_list) == 1 and strip_single_object_lists:
                result[k] = items_list[0]
            else:
                result[k] = items_list
    return result


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


def join_non_nulls(strings, delimiter=", "):
    return delimiter.join([s for s in strings if s is not None and s != ""])


def append_if_absent(l, i):
    if i not in l:
        l.append(i)
    return l


def add_to_list_in_dict(item, list_name, dictionary):
    append_if_absent(set_if_absent_and_get(dictionary, list_name, []), item)


def add_to_struct(key, item, struct):
    append_if_absent(set_if_absent_and_get(struct, key, []), item)


def all_combinations(list_of_keys, lists_of_lists_of_vals):
    return [dict(list(zip(list_of_keys, combo))) for combo in product(
        *lists_of_lists_of_vals)]


def is_subset_of(set1, set2):
    return all(el in set2 for el in set1)

def is_subdict_of(dict1, dict2, allow_sub_lists=False):
    for k, v in six.iteritems(dict1):
        if k not in dict2:
            return False
        if v != dict2[k]:
            if isinstance(v, dict):
                if not isinstance(dict2[k], dict) or not is_subdict_of(v, dict2[k]):
                    return False
            elif allow_sub_lists and (isinstance(v, list) or isinstance(v, set)):
                return is_subset_of(v, dict2[k])
            else:
                return False
    return True

    

# def difference_dict(dict1, dict2):
#     intersection_dict = {}
#     for k, v in dict1.iteritems():
#         if k in dict2:
#             if v == dict
#             if v != dict2[k]:
#                 if isinstance(v, dict):
#                     if not isinstance(dict2[k], dict) or not is_subdict_of(v, dict2[k]):
#                         return False
#                 elif allow_sub_lists and (isinstance(v, list) or isinstance(v, set)):
#                     return is_subset_of(v, dict2[k])
#                 else:
#                     return False
#     return True   

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

def boolean_or_of_dicts(*dicts):
    result = {}
    for d in dicts:
        for k, v in six.iteritems(d):
            result[k] = bool(result.get(k) or v)
    return result

def boolean_and_of_dicts(*dicts):
    result = {}
    for d in dicts:
        for k, v in six.iteritems(d):
            result[k] = bool(result.get(k) and v)
    return result

def batchiter(iterator, batch_size):
    batch = []
    for item in iterator:
        pass

def apply_function_on_leaf_nodes(func, *dicts):
    def adapt_func_to_dict_items(f):
        pass
    result = {}
    for d in dicts:
        for k, v in d.items():
            if isinstance(v, dict):
                if k not in result:
                    result[k] = {'func': adapt_func_to_dict_items, 'values': [v]}
                else:
                    result[k].append(v)
            elif isinstance(v, list):
                pass
            else:
                if k not in result:
                    result[k] = {'func': func, 'values': [v]}
                else:
                    result[k].append(v)


def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]