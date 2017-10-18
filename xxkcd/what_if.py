import datetime
import collections
import weakref
import random

from objecttools import ThreadedCachedProperty

from xxkcd import constants
from xxkcd._util import urlopen, make_mapping_proxy, range, str_is_bytes, coerce_, dead_weaklink
from xxkcd._html_parsing import ParseToTree

__all__ = ('WhatIf',)

ArchiveEntry = collections.namedtuple('ArchiveEntry', ('image', 'title', 'date'))
ArticlePart = collections.namedtuple('ArticlePart', ('type', 'value'))


class Archive(object):
    _archive = None
    _months = [
        'January', 'February', 'March', 'April', 'May', 'June', 'July',
        'August', 'September', 'October', 'November', 'December'
    ]

    @ThreadedCachedProperty
    def _length(self):
        return len(self.__get__())

    _length.can_delete = True

    def __get__(self, instance=0, owner=None):
        if instance is None:
            return self
        archive = Archive._archive
        if archive is not None:
            return make_mapping_proxy(archive)
        parser = ParseToTree()
        with urlopen(constants.what_if.archive) as http:
            data = http.read()
        tree = parser(data)
        archive = {}
        for i, archive_entry in enumerate(tree.find_all(Archive._is_archive_entry), 1):
            c = archive_entry.element_children
            image = constants.what_if.base + c[0].first_element_child.attr_dict['src']
            if str_is_bytes:
                image = image.encode('ascii')
            archive[i] = ArchiveEntry(
                image=image,
                title=c[1].first_element_child.children[0].children,
                date=self._parse_date(c[2].children[0].children)
            )
        article = Archive._archive = make_mapping_proxy(archive)
        return make_mapping_proxy(article)

    def __delete__(self, instance):
        Archive._archive = None
        del Archive._length

    def __len__(self):
        return self._length

    @staticmethod
    def _is_archive_entry(node):
        return node.cls == 'archive-entry'

    @classmethod
    def _parse_date(cls, date):
        month, day, year = date.split()
        month = cls._months.index(month)
        day = int(day[:-1])
        year = int(year)
        return datetime.date(year, month + 1, day)


class WhatIf(object):
    __slots__ = ('_article', '__weakref__', '__dict__')

    _cache = {}
    _keep_alive = {}

    archive = Archive()

    def __new__(cls, article=None, keep_alive=False):
        if isinstance(article, cls):
            if keep_alive:
                cls._keep_alive[article.article] = article
            return article
        article = coerce_(article, cls.latest)
        self = cls._cache.get(article, dead_weaklink)()
        if self is None:
            self = super(WhatIf, cls).__new__(cls)
            self._article = article
            cls._cache[article] = weakref.ref(self)
        if keep_alive:
            cls._keep_alive[article] = self
        return self

    @classmethod
    def latest(cls):
        return len(cls.archive)

    @classmethod
    def random(cls):
        return WhatIf(random.randint(1, cls.latest()))

    @property
    def article(self):
        return self._article

    @property
    def number(self):
        if self._article is None:
            return self.latest()
        return self._article

    @property
    def image(self):
        return self.archive[self.number].image

    img = image  # To remain consistent with the xkcd API

    @property
    def title(self):
        return self.archive[self.number].title

    @property
    def date(self):
        return self.archive[self.number].date

    @property
    def month(self):
        return self.date.month

    @property
    def day(self):
        return self.date.day

    @property
    def year(self):
        return self.date.year

    @staticmethod
    def news():
        with urlopen(constants.xkcd.c.what_if.news) as http:
            return http.read()

    @property
    def url(self):
        if self.article is None:
            return constants.what_if.latest
        return constants.what_if.for_article(number=self.article)

    @ThreadedCachedProperty
    def full_page(self):
        with urlopen(self.url) as http:
            return http.read().decode('utf-8')

    full_page.can_delete = True

    @ThreadedCachedProperty
    def _article_tree(self):
        tree = ParseToTree()(self.full_page)
        return tree.find(lambda node: node.tag.lower() == 'article' and node.cls == 'entry')

    _article_tree.can_delete = True

    @ThreadedCachedProperty
    def _article_node(self):
        return WhatIf()._article_tree.find(lambda a: a.cls == 'entry')

    _article_node.can_delete = True

    @ThreadedCachedProperty
    def question(self):
        return str(self._article_tree.get_element_by_id('question').children[0])

    question.can_delete = True

    @ThreadedCachedProperty
    def attribute(self):
        return str(
            self._article_tree.get_element_by_id('attribute').children[0]
        )

    attribute.can_delete = True

    @ThreadedCachedProperty
    def body(self):
        return str(self._article_node)

    body.can_delete = True

    def delete(self, remove_cache=True):
        del self.full_page
        del self._article_tree
        del self._article_node
        del self.question
        del self.attribute
        del self.body
        if remove_cache:
            self._keep_alive.pop(self.article, None)
            self._cache.pop(self.article, None)

    def refresh(self):
        self.delete(False)
        self.full_page
        self._article_tree
        self._article_node
        self.question
        self.attribute
        self.body

    def next(self):
        return self.__next__()

    def back(self):
        if self.article is None:
            return type(self)(self.latest() - 1)
        if self.article == 1:
            raise StopIteration
        return type(self)(self.article - 1)

    def __next__(self):
        if self.article is None or self.article == self.latest():
            raise StopIteration
        return type(self)(self.article + 1)

    def __reversed__(self):
        if self.article is None:
            comic = self.latest()
        else:
            comic = self.article
        for i in range(comic - 1, 0, -1):
            yield type(self)(i)

    @classmethod
    def range(cls, from_=1, to=None, step=1):
        if to is None:
            to = cls.latest() + 1
        return range(from_, to, step)

    def __eq__(self, other):
        if isinstance(other, WhatIf) and isinstance(self, WhatIf):
            if self is other or other.article == self.article:
                return True
            if self.article is None:
                return self.number == other.article
            if other.article is None:
                return other.number == self.article
            return False
        return NotImplemented

    def __ne__(self, other):
        eq = self.__eq__(other)
        if eq is NotImplemented:
            return NotImplemented
        return not eq

    def __lt__(self, other):
        if isinstance(other, WhatIf) and isinstance(self, WhatIf):
            if self is other or self.article == other.article:
                return False
            if self.article is None:
                return False
            if other.article is None:
                return True
            return self.article < other.article
        return NotImplemented

    def __le__(self, other):
        if isinstance(other, WhatIf) and isinstance(self, WhatIf):
            if self is other or self.article == other.article:
                return True
            if self.article is None:
                if other.article is None:
                    return True
                return self.number == other.article
            if other.article is None:
                return True
            return self.article <= other.article
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
