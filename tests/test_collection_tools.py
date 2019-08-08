from __future__ import absolute_import
import pytest

from toolspy import collection_tools


def test_unique_sublists_simple_case():
    lst = [1, 3, 5, 1, 3, 2, 6, 7, 90, 1, 7, 8]
    assert collection_tools.unique_sublists(lst) ==  [[1, 3, 5, 2, 6, 7, 90, 8], [1, 3, 7], [1]]

def test_delete_dict_keys_simple_case():
    d = {
        "id": 1,
        "name": "hello"
    }
    collection_tools.delete_dict_keys(d, ['id'])
    assert "id" not in d

def test_delete_dict_keys_non_existent_key():
    d = {
        "id": 1,
        "name": "hello"
    }
    collection_tools.delete_dict_keys(d, ['i'])
    assert "id" in d

def test_delete_dict_keys_nested_dict():
    d = {
        "id": 1,
        "name": "hello",
        "child": {
            "id": 5,
            "desc": "First child"
        }
    }
    collection_tools.delete_dict_keys(d, ['id', 'child.id'])
    assert "id" not in d['child']

def test_delete_dict_keys_nested_list():
    d = {
        "id": 1,
        "name": "hello",
        "children": [{
            "id": 5,
            "desc": "First child"
        }, {
            "id": 6,
            "desc": "Second child"
        }]
    }
    collection_tools.delete_dict_keys(d, ['id', 'children.id'])
    assert all("id" not in child for child in d["children"])