# coding: utf-8

import sys
import weakref
import json
import datetime
import random
import functools

from objecttools import ThreadedCachedProperty

from xxkcd._moves import urlopen, reload, unescape
from xxkcd import constants


_404_mock = {
    'month': '4', 'num': 404, 'link': '', 'year': '2008', 'news': '',
    'safe_title': '404 not found', 'transcript': '', 'alt': '', 'img': '',
    'title': '404 - Not Found', 'day': '1'
}


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
            return unescape(s)
    return unescape(s)

# Python 2 and Python 3.6+ allow bytes JSON
_JSON_BYTES = sys.version_info < (3,) or sys.version_info >= (3, 6)

class xkcd(object):
    """Interface with the xkcd JSON API"""
    __slots__ = ('_comic', '__weakref__', '__dict__')

    _cache = {}
    _keep_alive = {}

    def __new__(cls, comic=None, keep_alive=False):
        """
        Wrapper around the xkcd API for the comic

        :param Optional[int] comic: Number of the comic.
            Non-positive or `None` for the latest comic
        :param bool keep_alive: True to not delete the data requested until
            the `.delete()` method is called
        :return: The new xkcd object
        :rtype: xkcd
        :raises TypeError: Non-int given as comic
        """
        if comic is not None:
            try:
                comic = int(comic)
            except (ValueError, TypeError):
                raise TypeError('comic must be an integer')
            if comic <= 0 or comic > cls.latest():
                comic = None
        cached = cls._cache.get(comic, None)
        if cached is not None:
            cached = cached()
            if cached is not None:
                if keep_alive:
                    cls._keep_alive[comic] = cached
                return cached
        self = super(xkcd, cls).__new__(cls)
        self._comic = comic
        cls._cache[comic] = weakref.ref(self)
        if keep_alive:
            cls._keep_alive[comic] = self
        return self

    @property
    def comic(self):
        return self._comic

    @ThreadedCachedProperty
    def _raw_json(self):
        """Raw JSON with a possibly incorrect transcript and alt text"""
        if self.comic == 404:
            return _404_mock
        if self.comic is None:
            url = constants.xkcd.json.latest
        else:
            url = constants.xkcd.json.for_comic(number=self.comic)
        with urlopen(url) as http:
            if _JSON_BYTES:
                return json.load(http)
            return json.loads(http.read().decode('utf-8'))

    _raw_json.can_delete = True

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
        other_json = self._raw_json.copy()
        if n < self.latest() - 3:
            other_json['transcript'] = _decode(xkcd(n)._raw_json['transcript'])
        else:
            other_json['transcript'] = _decode(other_json['transcript'])
        for text_key in ('alt', 'title', 'safe_title'):
            other_json[text_key] = _decode(other_json[text_key])
        for int_key in ('day', 'month', 'year'):
            if other_json[int_key]:
                other_json[int_key] = int(other_json[int_key])
            else:
                other_json[int_key] = None
        if other_json['img'] == constants.xkcd.images.blank:
            other_json['img'] = ''
        return other_json

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
        with urlopen(self.img) as http:
            return http.read()

    def stream_image(self, file=None, chunk_size=2048):
        """
        Stream the raw image file from the link and write to file.

        :param file: File-like to write to, or None to yield chunks
        :type file: Optional[BinaryIO]
        :param chunk_size: Size of chunks
        :type chunk_size: int
        :return: generator or None
        """
        if not self.img:
            raise ValueError('Comic {} does not have an image!'.format(self))
        if file is None:
            def generator():
                with urlopen(self.img) as http:
                    for i in iter(functools.partial(http.read, chunk_size), b''):
                        yield i
            return generator()
        else:
            with urlopen(self.img) as http:
                for i in iter(functools.partial(http.read, chunk_size), b''):
                    file.write(i)

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
        return xkcd(keep_alive=True)._raw_json['num']

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
            return constants.Explainxkcd.latest
        return constants.Explainxkcd.for_comic(number=self.comic)

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
        return '{type.__name__}({number})'.format(type=type(self), number=self.comic or '')

    @property
    def next(self):
        """
        Return the next comic. If is the latest comic, return the same comic

        :return: Next comic
        :rtype: xkcd
        """
        if self.comic is None:
            return self
        return type(self)(self.comic + 1)

    @property
    def previous(self):
        """
        Return the previous comic. If is xkcd(1), return self.

        :return: Previous comic
        :rtype: xkcd
        """
        if self.comic is None:
            return type(self)(type(self).latest() - 1)
        if self.comic == 1:
            return self
        return type(self)(self.comic - 1)

    @staticmethod
    def antigravity():
        """???"""
        antigravity = sys.modules.get('antigravity')
        if antigravity is not None:
            return reload(antigravity)
        import antigravity
        return antigravity

    def __eq__(self, other):
        if isinstance(other, xkcd):
            if other.comic == self.comic:
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
