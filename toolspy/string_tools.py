from __future__ import absolute_import
import re
from random import choice
import six
from six.moves import range
import string


def random_string(length=8, candidates=None):
    if candidates is None:
        candidates = string.ascii_letters + string.digits
    return ''.join(choice(candidates) for _ in list(range(length)))


def npartition(string, n=1, delimiter=' '):
    """
    Similar to python's built in partition method. But will
    split at the nth occurence of delimiter
    """
    groups = string.split(delimiter)
    return (delimiter.join(groups[:n]), delimiter, delimiter.join(groups[n:]))


def is_email(mailstr):
    """
    Checks if a string matches the Email regex
    """
    EMAIL_REGEX = re.compile(r"[^@]+@[^@]+\.[^@]+")
    return ((isinstance(mailstr, str) or isinstance(mailstr, six.text_type))
            and bool(EMAIL_REGEX.match(mailstr)))


def capitalize_words(sentence):
    return ' '.join(word.capitalize() for word in sentence.split(" "))


def strip_bad_chars(string, chars=[' ', '_', ';', ',', '"', "'"]):
    for char in chars:
        string = string.replace(char, '')
    return string


def abbreviated_name(name, append_digit=None, length=6):
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
            return word[0]+[l for l in word[1:-1] if l not in vowels] + word[-1]
        else:
            return word

    concatenate = ''.join

    abbr = concatenate([strip_vowels(word) for word in words_of(
        name.upper())])[0:length]

    if append_digit:
        abbr = abbr+str(append_digit)

    return abbr
