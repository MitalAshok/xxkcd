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
    try:
        from types import DictProxyType as MappingProxyType
    except ImportError:
        MappingProxyType = None

try:
    MappingProxyType({'a': None})['a']
except:
    MappingProxyType = None

if MappingProxyType is None:
    class MappingProxyType(object):
        __slots__ = ('_m')

        def __init__(self, mapping):
            self._m = mapping

        def __cmp__(self, other):
            return cmp(self._m, other)

        def __contains__(self, key):
            return key in self._m

        def __eq__(self, other):
            return self._m == other

        def __ge__(self, other):
            return self._m > other

        def __getitem__(self, key):
            return self._m[key]

        def __gt__(self, other):
            return self._m > other

        def __iter__(self):
            return iter(self._m)

        def __le__(self, other):
            return self._m <= other

        def __len__(self):
            return len(self._m)

        def __lt__(self, other):
            return self._m < other

        def __ne__(self, other):
            return self.m != other

        def __repr__(self):
            return '{}({!r})'.format(type(self).__name__, self._m)

        def copy(self):
            return self._m.copy()

        def get(self, key, default=None):
            return self._m.get(key, default)

        def has_key(self, key):
            return self._m.has_key(key)

        def items(self):
            return self._m.items()

        def iteritems(self):
            return self._m.iteritems()

        def iterkeys(self):
            return self._m.iterkeys()

        def itervalues(self):
            return self._m.itervalues()

        def keys(self):
            return self._m.keys()

        def values(self):
            return self._m.values()


def make_mapping_proxy(mapping):
    if isinstance(mapping, MappingProxyType):
        return mapping
    return MappingProxyType(mapping)


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

str_is_unicode = str_type is text_type
str_is_bytes = str_type is binary_type

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
short = builtins.int

try:
    from operator import index
except ImportError:
    def index(o):
        return range(o)[-1] + 1  # Use xrange to coerce to integer

try:
    infinity = float('inf')
except ValueError:
    infinity = 1e999 ** 2
neg_infinity = -infinity

_probably_exists = 1951


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
        try:
            x = short(x)
        except:
            pass
        if x == 0:
            return None
        if x <= 0:
            x = max_fn() + 1 + x
            if x <= 0:
                return 1
            return x
        if x <= _probably_exists:
            return x
        return min(x, max_fn())
    raise TypeError('comic must be an integer')
