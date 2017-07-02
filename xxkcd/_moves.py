import contextlib

try:
    from urllib.request import urlopen
    from html.parser import HTMLParser
    from types import MappingProxyType
except ImportError:
    from urllib2 import urlopen as _urlopen
    from HTMLParser import HTMLParser

    def urlopen(*args, **kwargs):
        return contextlib.closing(_urlopen(*args, **kwargs))

    MappingProxyType = dict.copy

try:
    from html import unescape  # Python 3.4+
except ImportError:
    unescape = HTMLParser().unescape

text_type = type(u'')
binary_type = type(b'')

try:
    from importlib import reload
except ImportError:
    from __builtin__ import reload
