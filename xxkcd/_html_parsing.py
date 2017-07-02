import collections

from ._moves import HTMLParser, text_type


class HTMLNode(collections.namedtuple('HTMLNode', ('tag', 'attrs', 'children', 'parent'))):
    def find(self, criteria):
        return next(self.find_all(criteria), None)

    def find_all(self, criteria):
        queue = collections.deque()
        queue.append(self)
        while queue:
            current = queue.popleft()
            if isinstance(current, text_type):
                continue
            if criteria(current):
                yield current
            queue.extend(current.children)

    def root(self):
        node = self
        while node.parent is not None:
            node = node.parent
        return node

    @property
    def cls(self):
        return self.attr_dict.get('class', '')

    @property
    def first_element_child(self):
        for child in self.children:
            if child.tag != '<text>':
                return child
        return None

    @property
    def element_children(self):
        return [child for child in self.children if child.tag != '<text>']

    @property
    def attr_dict(self):
        return dict(reversed(self.attrs))

    @property
    def id(self):
        return self.attr_dict.get('id', None)

    def get_element_by_id(self, id):
        return self.find(lambda node: node.id == id)

    def __repr__(self):
        if self.tag == '<text>':
            return '<TextNode {!r}>'.format(self.children)
        return ('<HTMLNode tag={tag} attrs={attrs} children=[{children}] '
                'parent={parent}>').format(
            tag=self.tag, attrs=self.attrs, children=', '.join(
                '<{}/>'.format(n.tag) if n.tag != '<text>' else repr(n)
                for n in self.children
            ), parent=self.parent and '<{}/>'.format(self.parent.tag)
        )

class ParseToTree(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self._entry = self.tree = HTMLNode('_root', [], [], None)

    def handle_starttag(self, tag, attrs):
        new_entry = HTMLNode(tag.lower(), attrs, [], self._entry)
        self._entry.children.append(new_entry)
        self._entry = new_entry

    def handle_endtag(self, tag):
        while self._entry.tag != tag.lower():
            self._entry = self._entry.parent
        self._entry = self._entry.parent

    def handle_data(self, data):
        self._entry.children.append(HTMLNode('<text>', [], data, self._entry))

    def reset(self):
        self._entry = self.tree = HTMLNode('_root', [], [], None)
        HTMLParser.reset(self)

    def __call__(self, text):
        self.reset()
        if not isinstance(text, text_type):
            text = text.decode('utf-8')
        self.feed(text)
        self.close()
        parsed = self.tree
        self.reset()
        return parsed
