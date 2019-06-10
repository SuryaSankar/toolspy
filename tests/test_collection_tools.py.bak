import pytest

from toolspy import collection_tools


def test_unique_sublists_simple_case():
    lst = [1, 3, 5, 1, 3, 2, 6, 7, 90, 1, 7, 8]
    assert collection_tools.unique_sublists(lst) == [[1, 3]]
