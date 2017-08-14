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
