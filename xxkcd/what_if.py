import datetime
import collections
import weakref
import random

from objecttools import ThreadedCachedProperty

from xxkcd import constants
from xxkcd._moves import urlopen, MappingProxyType
from xxkcd._html_parsing import ParseToTree

ArchiveEntry = collections.namedtuple('ArchiveEntry', ('image', 'title', 'date'))

has_unicode = type(u'') is type('')

class Archive(object):
    _archive = None
    _months = [
        'January', 'February', 'March', 'April', 'May', 'June', 'July',
        'August', 'September', 'October', 'November', 'December'
    ]

    def __get__(self, instance, owner):
        if Archive._archive is not None:
            return Archive._archive
        parser = ParseToTree()
        with urlopen(constants.WhatIf.archive) as http:
            data = http.read()
        tree = parser(data)
        archive = {}
        i = 0
        for i, archive_entry in enumerate(tree.find_all(Archive._is_archive_entry), 1):
            c = archive_entry.element_children
            image = constants.WhatIf.base + c[0].first_element_child.attr_dict['src']
            if has_unicode:
                image = image.encode('ascii')
            archive[i] = ArchiveEntry(
                image=image,
                title=c[1].first_element_child.children[0].children,
                date=self._parse_date(c[2].children[0].children)
            )
        archive['entries'] = i
        Archive._archive = MappingProxyType(archive)
        return Archive._archive

    def __delete__(self, instance):
        Archive._archive = None

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

    def __new__(cls, article=None, keep_alive=False):
        if article is not None:
            try:
                article = int(article)
            except (ValueError, TypeError):
                raise TypeError('article must be an integer')
            if article <= 0 or article > cls.latest():
                article = None
        cached = cls._cache.get(article, None)
        if cached is not None:
            cached = cached()
            if cached is not None:
                if keep_alive:
                    cls._keep_alive[article] = cached
                return cached
        self = super(WhatIf, cls).__new__(cls)
        self._article = article
        cls._cache[article] = weakref.ref(self)
        if keep_alive:
            cls._keep_alive[article] = self
        return self

    archive = Archive()

    @classmethod
    def latest(cls):
        return cls.archive['entries']

    @classmethod
    def random(cls):
        return WhatIf(random.randint(1, cls.latest()))

    @property
    def article(self):
        return self._article

    @property
    def image(self):
        return self.archive[self.article or self.latest()].image

    img = image  # To remain consistent with the xkcd API

    @property
    def title(self):
        return self.archive[self.article or self.latest()].title

    @property
    def date(self):
        return self.archive[self.article or self.latest()].date

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
        with urlopen(constants.xkcd.c.whatif.news) as http:
            return http.read()

    @property
    def url(self):
        if self.article is None:
            return constants.WhatIf.latest
        return constants.WhatIf.for_article(number=self.article)

    @ThreadedCachedProperty
    def full_page(self):
        with urlopen(self.url) as http:
            return http.read()

    full_page.can_delete = True

    @ThreadedCachedProperty
    def _article_tree(self):
        tree = ParseToTree()(self.full_page)
        return tree.find(lambda node: node.tag.lower() == 'article' and node.cls == 'entry')

    _article_tree.can_delete = True

    @ThreadedCachedProperty
    def question(self):
        return self._article_tree.get_element_by_id('question').children[0].children

    question.can_delete = True

    @ThreadedCachedProperty
    def attribute(self):
        return self._article_tree.get_element_by_id('attribute').children[0].children

    attribute.can_delete = True

    def body(self):
        return NotImplemented

    def delete(self):
        del self.full_page
        del self._article_tree
        del self.question
        self._keep_alive.pop(self.article, None)
        self._cache.pop(self.article, None)
