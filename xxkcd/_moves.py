import contextlib

try:
    from urllib.request import urlopen
except ImportError:
    from urllib2 import urlopen as _urlopen
    def urlopen(*args, **kwargs):
        return contextlib.closing(_urlopen(*args, **kwargs))

try:
    from importlib import reload
except ImportError:
    from __builtin__ import reload
