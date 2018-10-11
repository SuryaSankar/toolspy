
def random_string(length=8, candidates='ABCDEFGHIJKLMNPQRSTUVWXYZ123456789'):
    return ''.join(choice(candidates) for i in range(length))


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
    return ((isinstance(mailstr, str) or isinstance(mailstr, unicode))
            and bool(EMAIL_REGEX.match(mailstr)))