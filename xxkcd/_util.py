# Compatibility

try:
    import builtins
except ImportError:
    import __builtin__ as builtins

try:
    from urllib.request import urlopen
except ImportError:
    from urllib2 import urlopen as _urlopen
    import contextlib

    def urlopen(*args, **kwargs):
        return contextlib.closing(_urlopen(*args, **kwargs))

try:
    from html.parser import HTMLParser
except ImportError:
    from HTMLParser import HTMLParser

try:
    from types import MappingProxyType
except ImportError:
    MappingProxyType = dict

try:
    from html import unescape  # Python 3.4+
except ImportError:
    unescape = HTMLParser().unescape

try:
    from html import escape
except ImportError:
    def escape(s, quote=True):
        s = s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        if quote:
            return s.replace('"', '&quot;').replace("'", '&#x27;')
        return s


text_type = type(u'')
str_type = type('')
binary_type = type(b'')

str_is_unicode = text_type is text_type
str_is_bytes = text_type is binary_type

try:
    from importlib import reload
except ImportError:
    reload = builtins.reload

try:
    from itertools import imap as map, ifilter as filter, izip as zip
except ImportError:
    map = builtins.map
    zip = builtins.zip
    filter = builtins.filter

try:
    from functools import reduce
except ImportError:
    reduce = builtins.reduce

range = getattr(builtins, 'xrange', range)
int = getattr(builtins, 'long', int)

try:
    from operator import index
except ImportError:
    index = int

try:
    infinity = float('inf')
    neg_infinity = -infinity
except ValueError:
    infinity = None
    neg_infinity = None

def dead_weaklink():
    return None

def coerce_(x, max_fn):
    if x is None:
        return x
    try:
        x = int(index(x))
    except (ValueError, TypeError):
        try:
            x = float(x)
            if x >= infinity:
                return None
        except (ValueError, TypeError):
            pass
    else:
        if x == 0:
            return None
        if x <= 0:
            x = max_fn() + 1 + x
            if x <= 0:
                return 1
            return x
        return min(x, max_fn())
    raise TypeError('comic must be an integer')
