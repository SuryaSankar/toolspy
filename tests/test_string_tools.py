from __future__ import absolute_import
import pytest

from toolspy import string_tools


def test_npartition_simple_case():
    test_str = "Hello world 1234"
    assert string_tools.npartition(
        test_str, n=2) == ("Hello world", " ", "1234")


def test_npartition_with_different_delim():
    test_str = "Hello|World 123|New |Line"
    assert string_tools.npartition(test_str, n=3, delimiter="|") == (
        "Hello|World 123|New ", "|", "Line"
    )
