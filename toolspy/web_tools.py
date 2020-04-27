from __future__ import absolute_import
try:
    from six.moves.urllib.parse import urlencode
    from six.moves.urllib.parse import parse_qs, urlsplit, urlunsplit
except:
    pass


# Lifted from http://stackoverflow.com/a/12897375
def set_query_params(url, params):
    """Given a URL, set or replace a query parameter and return the
    modified URL.

    >>> set_query_parameter('http://example.com?foo=bar&biz=baz', 'foo', 'stuff')
    'http://example.com?foo=stuff&biz=baz'

    """
    if url is None:
        return None
    if params is None:
        return url
    scheme, netloc, path, query_string, fragment = urlsplit(url)
    query_params = parse_qs(query_string)
    for param_name, param_value in params.items():
        query_params[param_name] = [param_value]
    new_query_string = urlencode(query_params, doseq=True)

    return urlunsplit((scheme, netloc, path, new_query_string, fragment))


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


def get_query_params(url, one_value_per_param=True):
    result = parse_qs(urlsplit(url).query)
    if one_value_per_param:
        result = {k: v[0] for k, v in result.items()}
    return result

