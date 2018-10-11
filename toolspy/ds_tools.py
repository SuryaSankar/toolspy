from collections import defaultdict

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

def merge_lists_in_same_order(list_of_lists):
    final_list = []
    successors = defaultdict(list)

    for lst in list_of_lists:
        for idx, item in enumerate(lst):
            for successor in lst[idx+1:]:
                if successor not in successors[item]:
                    successors[item].append(successor)
                if successor in successors:
                    for secondary_successor in successors[successor]:
                         
    print successors
    ranks = defaultdict(list)
    for k, v in successors.items():
        ranks[len(v)].append(k)
    print ranks
    return (successors, ranks)



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
        preceding_items = remove_duplicates(flatten([preceding_items_list(l, item) for l in list_of_lists]))
        for p_item in preceding_items:
            if p_item in item_predecessors and item in item_predecessors[p_item]:
                preceding_items.remove(p_item)
        item_predecessors[item] = preceding_items

    items_to_be_checked = difference(unique_items, item_priorities.keys())
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
                    item_priorities[item] = max([item_priorities[p] for p in predecessors]) + 1
                    # print "Set priority of item to %s" % item_priorities[item]
                else:
                    # print "Doing nothing for ", item
        # print "item_priorities at end of loop ", item_priorities
        items_to_be_checked = difference(unique_items, item_priorities.keys())
        # print "items to be checked at end of loop ", items_to_be_checked
        # print

    final_list = sorted(unique_items, key=lambda item: item_priorities.get(item) or 0)
    return final_list

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

def dict_map(d, mapper):
    return {k: mapper(v) for k, v in d.iteritems()}


def flatten(list_of_lists):
    """
    >>> flatten([[1,2], [3,4,5]])
    [1, 2, 3, 4, 5]
    """
    return [item for sublist in list_of_lists for item in sublist]


def filtered_list(olist, exclude_list):
    return filter(lambda i: i not in exclude_list, olist)
        