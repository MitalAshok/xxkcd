import collections

import objecttools

from xxkcd._util import HTMLParser, text_type, map, escape


@objecttools.Singleton.as_decorator
class TextNode(str):
    def __new__(cls):
        return str.__new__(TextNode, '<text>')

    def __repr__(self):
        return 'text_node'

text_node = TextNode()


class HTMLNode(
    collections.namedtuple('HTMLNode', ('tag', 'attrs', 'children', 'parent'))
):
    def find(self, criteria):
        return next(self.find_all(criteria), None)

    def find_all(self, criteria):
        queue = collections.deque()
        queue.append(self)
        while queue:
            current = queue.popleft()
            if criteria(current):
                yield current
            if current.tag is not text_node:
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
            if child.tag is not text_node:
                return child
        return None

    @property
    def element_children(self):
        return [child for child in self.children if child.tag is not text_node]

    @property
    def attr_dict(self):
        return dict(reversed(self.attrs))

    @property
    def id(self):
        return self.attr_dict.get('id', None)

    def get_element_by_id(self, id):
        return self.find(lambda node: node.id == id)

    def __repr__(self):
        if self.tag is text_node:
            return '<TextNode {!r}>'.format(self.children)
        if self.parent is None:
            parent = None
        elif self.parent.tag is text_node:
            parent = repr(self.parent)
        else:
            parent = '<{}/>'.format(self.parent.tag)
        children = ', '.join(
            '<{}/>'.format(n.tag) if n.tag is not text_node else repr(n)
            for n in self.children
        )
        return (
            '<HTMLNode tag={self.tag} attrs={self.attrs} '
            'children=[{children}] parent={parent}>'
        ).format(self=self, children=children, parent=parent)

    def __str__(self):
        if self.tag is text_node:
            return self.children
        if self.attrs:
            attrs = ' ' + ' '.join('{}="{}"'.format(attr, escape(value)) for attr, value in self.attrs)
        else:
            attrs = ''
        return '<{self.tag}{attrs}>{contents}</{self.tag}>'.format(
            self=self, attrs=attrs,
            contents=u''.join(map(text_type, self.children))
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
        self._entry.children.append(HTMLNode(text_node, [], data, self._entry))

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
