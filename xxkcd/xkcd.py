# coding: utf-8

import sys
import weakref
import json
import datetime
import random
import functools
import posixpath
import multiprocessing
import shutil
import contextlib

from objecttools import ThreadedCachedProperty

from xxkcd._util import (
    urlopen, reload, unescape, map, str_is_bytes, make_mapping_proxy,
    range, short, dead_weaklink, coerce_, text_type
)
from xxkcd import constants

__all__ = ('xkcd',)

_404_mock = make_mapping_proxy({
    'month': 4, 'num': 404, 'link': '', 'year': 2008, 'news': u'',
    'safe_title': u'404 not found', 'transcript': u'', 'alt': u'', 'img': '',
    'title': u'404 - Not Found', 'day': 1
})


def _decode(s):
    """
    Decodes the incorrect encoding used in the xkcd JSON api.

    All of the fields of xkcd comics that use non-ascii characters incorrectly
    encode binary UTF-8 as escaped UTF-8.

    For example, 'é' -> 0xC3 0xA9 -> '\\u00c3\\u00a9' in the JSON, which
    actually encodes 'Ã©'

    This is sometimes done multiple times, like in xkcd(124).

    :param str s: String to decode
    :return: Decoded string
    :rtype: Text
    """
    for _ in range(10):
        try:
            s = bytearray(map(ord, s)).decode('utf-8')
        except (ValueError, UnicodeDecodeError):
            break
    return unescape(s)


# Python 2 and Python 3.6+ allow bytes JSON
_JSON_BYTES = sys.version_info < (3,) or sys.version_info >= (3, 6)

if not _JSON_BYTES:
    import codecs

    _UTF_8_READER = codecs.getreader('utf-8')

_MIMES = {
    'png': 'image/png', 'jpg': 'image/jpeg', 'gif': 'image/gif',
    'jpeg': 'image/jpeg'
}


___ = 'antigravity'
____ = sys.modules.get
_____ = None
______ = reload


def _loader(cls, n):
    return dict(cls(n)._raw_json)


class xkcd(object):
    """Interface with the xkcd JSON API"""
    __slots__ = ('_comic', '__weakref__', '__dict__')

    urlopen = staticmethod(urlopen)

    _cache = {}
    _keep_alive = {}

    def __new__(cls, comic=None, keep_alive=False):
        """
        Wrapper around the xkcd API for the comic

        :param Union[int, None, xkcd] comic: Number of the comic.
            -1 or `None` for the latest comic.
            -x means x comics before the latest comic.
        :param bool keep_alive: True to not delete the data requested until
            the `.delete()` method is called
        :return: The new xkcd object
        :rtype: xkcd
        :raises TypeError: Non-int given as comic
        """
        if isinstance(comic, xkcd):
            comic = comic.comic
        else:
            comic = coerce_(comic, cls.latest)
        self = cls._cache.get(comic, dead_weaklink)()
        if self is None:
            self = super(xkcd, cls).__new__(cls)
            self._comic = comic
            cls._cache[comic] = weakref.ref(self)
        if keep_alive:
            cls._keep_alive[comic] = self
        return self

    @staticmethod
    def with_opener(opener, name='xkcdWithCustomOpener', module=__name__, qualname=None):
        """
        Takes an opener and returns an xkcd subclass that makes HTTP requests with that opener.

        The opener is a callable object (e.g. a type). When called with a `str` for the
        url, it should return an object with the following methods:
            `read(n: int)`: Returns that many bytes from the response from the url.
            `read()`: Read from the request and return as many bytes as possible.
            `close()`: Closes the connection and no more methods will be called before open.

        There may be more than one open connection at a time.

        For example:

            import requests

            class Opener(object):
                __slots__ = ('response',)

                _session = None

                @classmethod
                def get(cls, url):
                    if cls._session is None:
                        cls._session = requests.Session()
                    return cls._session.get(url)

                def __init__(self, url):
                    self.response = self.get(self._url)

                def read(self, n=None):
                    if n is None:
                        return self.response.content
                    return self.response.raw.read(n)

                def close(self):
                    self.response.close()

        :param opener: The opener, as described above.
        :param str name: The name of the subclass.
        :param str module: The module of the new type.
        :param Optional[str] qualname: The qualified name of the class.
          Defaults to `module + '.' + name`.
        """
        @staticmethod
        def urlopen(url):
            return contextlib.closing(opener(url))

        d = {
          '__slots__': xkcd.__slots__,
          'urlopen': urlopen,
          '_cache': {},
          '_keep_alive': {},
          '__module__': module
        }

        if hasattr(object, '__qualname__'):
            if qualname is None:
                qualname = module + '.' + name
            d['__qualname__'] = qualname
            urlopen.__qualname__ = qualname + '.urlopen'
        return type(name, (xkcd,), d)

    @property
    def comic(self):
        return self._comic

    @ThreadedCachedProperty
    def _raw_json(self):
        """Raw JSON with a possibly incorrect transcript and alt text"""
        if self.comic == 404:
            return make_mapping_proxy(_404_mock)
        if self.comic is None:
            url = constants.xkcd.json.latest
        else:
            url = constants.xkcd.json.for_comic(number=self.comic)
        with self.urlopen(url) as http:
            if not _JSON_BYTES:
                http = _UTF_8_READER(http)
            return make_mapping_proxy(json.load(http))

    _raw_json.can_delete = True
    _raw_json.can_set = True

    @ThreadedCachedProperty
    def json(self):
        """
        JSON with the correct transcript and encoded properly.

        Note, that in Python 2, all of the `str` keys are `unicode`.

        Format::
        {
            'month': (the number of the month it was published. Possibly None.),
            'num': (int of the number of the comic),
            'link': (str of where the comic links to when clicked on, most commonly a larger version),
            'year': (the year it was published. Possibly None.),
            'news': (str of news that would be placed on the news ticker on the comic. Usually empty.),
            'safe_title': (str of url safe title),
            'transcript': (str of the transript. Possibly empty, usually for later comics),
            'alt': (str of the text that appears in the title attribute of the comic. Possibly empty.),
            'img': (str of the direct link to the image. Possibly empty, usually for interactive comics),
            'title': (str of the original title of the comic.),
            'day': (the number of the day it was published. Possibly None.)
        }

        Type stub::
        {
            'month': Optional[int], 'num': int, 'link': Text,
            'year': Optional[int], 'news': Text, 'safe_title': Text,
            'transcript': Text, 'alt': Text, 'img': Text, 'title': Text,
            'day' Optional[int]
        }
        """
        n = self.comic
        if n is None:
            pass
        # These comics messed up the transcripts.
        # They were interactive comics that didn't have a transcript that
        # pushed the transcripts for all other comics 1 or 2 ahead.
        elif n >= 1663:
            n += 3
        elif n >= 1608:
            n += 2
        if str_is_bytes:
            other_json = {}
            for key in self._raw_json:
                other_json[key.encode('ascii')] = self._raw_json[key]
        else:
            other_json = dict(self._raw_json)
        if n is not None and n < self.latest() - 3:
            other_json['transcript'] = _decode(xkcd(n)._raw_json['transcript'])
        else:
            other_json['transcript'] = _decode(other_json['transcript'])
        for text_key in ('alt', 'title', 'safe_title'):
            other_json[text_key] = _decode(other_json[text_key])
        for int_key in ('day', 'month', 'year'):
            if other_json[int_key]:
                other_json[int_key] = short(other_json[int_key])
            else:
                other_json[int_key] = None
        if other_json['img'] == constants.xkcd.images.blank:
            other_json['img'] = ''
        if str_is_bytes:
            other_json['img'] = other_json['img'].encode('ascii')
            other_json['link'] = other_json['link'].encode('ascii')
        return make_mapping_proxy(other_json)

    json.can_delete = True

    @property
    def month(self):
        return self.json['month']

    @property
    def link(self):
        return self.json['link']

    @property
    def year(self):
        return self.json['year']

    @property
    def news(self):
        return self.json['news']

    @property
    def safe_title(self):
        return self.json['safe_title']

    @property
    def transcript(self):
        return self.json['transcript']

    @property
    def alt(self):
        return self.json['alt']

    @property
    def img(self):
        return self.json['img']

    def read_image(self):
        """
        Read the raw image from the link and return the data.

        :raises ValueError: Comic doesn't have an image (e.g., it is xkcd(404), or it is interactive.)
        :return: Raw image data
        :rtype: bytes
        """
        if not self.img:
            raise ValueError('Comic {} does not have an image!'.format(self))
        with self.urlopen(self.img) as http:
            # http.read may not read all at once.
            return b''.join(iter(http.read, b''))

    def stream_image(self, file=None, chunk_size=16384):
        """
        Stream the raw image file from the link and write to file.

        :param file: File-like to write to, or None to return an iterator over the chunks
        :type file: Optional[BinaryIO]
        :param chunk_size: Size of chunks (or None for the whole file in a single chunk. Consider `self.read_image()`.)
        :type chunk_size: Optional[int]
        :return: iterator or None
        :rtype: Optional[Iterator[bytes]]
        """
        if not self.img:
            raise ValueError('Comic {} does not have an image!'.format(self))
        opened = self.urlopen(self.img)
        if file is None:
            if chunk_size is None:
                with opened as http:
                    return iter((b''.join(iter(http.read, b'')),))
            def _generator():
                # Use an inner function so the function
                # can end normally if file is not None
                with opened as http:
                    read = functools.partial(http.read, chunk_size)
                    for chunk in iter(read, b''):
                        yield chunk
            return _generator()
        else:
            with opened as http:
                if chunk_size is None:
                    file.write(b''.join(iter(http.read, b'')))
                else:
                    shutil.copyfileobj(http, file, chunk_size)

    @property
    def image_filename(self):
        """Suggested name for the image file. None if no image."""
        if not self.img:
            return None
        return posixpath.basename(self.img)

    @property
    def image_ext(self):
        """File extension of image file. Usually '.png'. '' if no extension, None if no image."""
        image_name = self.image_filename
        if image_name is None:
            return None
        return posixpath.splitext(image_name)[1]

    @property
    def image_name(self):
        """`self.image_filename` without the extension."""
        image_name = self.image_filename
        if image_name is None:
            return None
        return posixpath.splitext(image_name)[0]

    @property
    def image_mime(self):
        """
        Mime type of the image. Usually 'image/png'.
        'application/octet-stream' if not found, None if no image.
        """
        ext = self.image_ext
        if ext is None:
            return None
        return _MIMES.get(ext.lstrip('.').lower(), 'application/octet-stream')

    @property
    def title(self):
        return self.json['title']

    @property
    def day(self):
        return self.json['day']

    @property
    def date(self):
        """
        :return: The day, month and year the comic was published.
        :rtype: datetime.date
        """
        return datetime.date(self.year, self.month, self.day)

    @classmethod
    def latest(cls):
        """
        :return: The number of the latest comic
        :rtype: int
        """
        return cls(keep_alive=True)._raw_json['num']

    @classmethod
    def random(cls):
        """
        :return: A random comic
        :rtype: xkcd
        """
        return cls(random.randint(1, cls.latest()))

    def delete(self):
        """
        Deletes the data associated with this xkcd object so that it is reloaded
        the next time it is requested

        :return: None
        """
        del self._raw_json
        del self.json
        self._keep_alive.pop(self.comic, None)
        self._cache.pop(self.comic, None)

    @property
    def explain_xkcd(self):
        """
        :return: The explain xkcd wiki link for this comic
        :rtype: str
        """
        if self.comic is None:
            return constants.explain_xkcd.latest
        return constants.explain_xkcd.for_comic(number=self.comic)

    @property
    def url(self):
        """
        :return: The url for this comic
        :rtype: str
        """
        if self.comic is None:
            return constants.xkcd.latest
        return constants.xkcd.for_comic(number=self.comic)

    @property
    def mobile_url(self):
        """
        :return: The mobile url for this comic
        :rtype: str
        """
        if self.comic is None:
            return constants.xkcd.mobile.latest
        return constants.xkcd.mobile.for_comic(number=self.comic)

    @property
    def num(self):
        return self.json['num']

    def __repr__(self):
        n = self.comic
        n = '' if n is None else n
        return '{type.__name__}({number})'.format(type=type(self), number=n)

    @classmethod
    def load_all(cls, multiprocessed=False):
        """
        Load all the comics into the cache. Note: Takes a lot of time.

        :param bool multiprocessed: Use multiprocessing.Pool instead of
            running in sequence
        :return: None
        """
        if multiprocessed:
            pool = multiprocessing.Pool(4)
            data = pool.map(cls._loader, cls.range())
            pool.close()
            pool.join()
            for n, raw_json in enumerate(data, 1):
                cls(n, keep_alive=True)._raw_json = make_mapping_proxy(raw_json)

        else:
            for n in cls.range():
                cls(n, keep_alive=True)._raw_json

    if sys.version_info >= (3,):
        _loader = classmethod(_loader)
    else:
        # Very hacky, but lets
        # _loader be a "bound" classmethod

        class _LoaderDescriptor(object):
            def __get__(self, instance, owner):
                return functools.partial(_loader, owner)

        _loader = _LoaderDescriptor()

    @classmethod
    def load_one(cls, n):
        cls(n, keep_alive=True)._raw_json

    @classmethod
    def delete_all(cls):
        cls().delete()
        for n in cls.range():
            cls(n).delete()

    @classmethod
    def delete_one(cls, comic):
        cls(comic).delete()

    @staticmethod
    def antigravity():
        """???"""
        antigravity = ____(___)
        if antigravity is not _____:
            return ______(antigravity)
        import antigravity
        return antigravity

    def __iter__(self):
        if self.comic is None:
            return iter((self,))
        cls = type(self)
        return map(cls, range(self.comic, cls.latest() + 1))

    def next(self, keep_alive=False):
        """
        Return the next comic. If is the latest comic, raise StopIteration

        :return: Next comic
        :rtype: xkcd
        """
        return self.__next__(keep_alive)

    def back(self, keep_alive=False):
        """
        Return the previous comic. If is xkcd(1), raise StopIteration.

        :return: Previous comic
        :rtype: xkcd
        """
        if self.comic is None:
            return type(self)(self.latest() - 1, keep_alive)
        if self.comic == 1:
            raise StopIteration
        return type(self)(self.comic - 1, keep_alive)

    def __next__(self, keep_alive=False):
        if self.comic is None or self.comic == self.latest():
            raise StopIteration
        return type(self)(self.comic + 1, keep_alive)

    def __reversed__(self):
        if self.comic is None:
            comic = self.latest()
        else:
            comic = self.comic
        cls = type(self)
        for i in range(comic - 1, 0, -1):
            yield cls(i)

    @classmethod
    def range(cls, from_=1, to=None, step=1):
        """
        Returns an iterator over specified comics.

        Use negative numbers to specify from the end.

        :param int from_: The comic to start from. Defaults to the first.
        :param Optional[int] to_: The comic to end by (exclusive). Defaults to last + 1.
        :param int step: The step amount. Defaults to one.
        :return: A range over the requested comics.
        """
        if to is None:
            if step < 0:
                to = 0
            else:
                to = cls.latest() + 1

        return range(from_, to, step)

    def __eq__(self, other):
        if isinstance(other, xkcd) and isinstance(self, xkcd):
            if self is other or other.comic == self.comic:
                return True
            if self.comic is None:
                return self.num == other.comic
            if other.comic is None:
                return other.num == self.comic
            return False
        return NotImplemented

    def __ne__(self, other):
        eq = self.__eq__(other)
        if eq is NotImplemented:
            return NotImplemented
        return not eq

    def __lt__(self, other):
        if isinstance(other, xkcd) and isinstance(self, xkcd):
            if self is other or self.comic == other.comic:
                return False
            if self.comic is None:
                return False
            if other.comic is None:
                return True
            return self.comic < other.comic
        return NotImplemented

    def __le__(self, other):
        if isinstance(other, xkcd) and isinstance(self, xkcd):
            if self is other or self.comic == other.comic:
                return True
            if self.comic is None:
                if other.comic is None:
                    return True
                return self.num == other.comic
            if other.comic is None:
                return True
            return self.comic <= other.comic
        return NotImplemented

    def __ge__(self, other):
        lt = self.__lt__(other)
        if lt is NotImplemented:
            return NotImplemented
        return not lt

    def __gt__(self, other):
        le = self.__le__(other)
        if le is NotImplemented:
            return NotImplemented
        return not le
