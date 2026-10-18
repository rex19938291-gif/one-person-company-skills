"""HTML 解析器（nconv.py 用）：保留實體字、屬性順序，可逐字往返。"""
from html.parser import HTMLParser

VOID = {'img','br','hr','input','meta','link','source','wbr','path','circle','rect','line','polyline','polygon','use','stop','ellipse'}

class Node:
    def __init__(self, tag=None, attrs=None, parent=None):
        self.tag = tag; self.attrs = attrs or []; self.children = []; self.parent = parent
    def elements(self): return [c for c in self.children if isinstance(c, Node)]
    def has_real_text(self): return any(isinstance(c, tuple) and c[1].strip() for c in self.children)

class DomBuilder(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=False)
        self.root = Node('#root'); self.cur = self.root
    def handle_starttag(self, tag, attrs):
        n = Node(tag, attrs, self.cur); self.cur.children.append(n)
        if tag not in VOID: self.cur = n
    def handle_startendtag(self, tag, attrs):
        self.cur.children.append(Node(tag, attrs, self.cur))
    def handle_endtag(self, tag):
        c = self.cur
        while c is not self.root and c.tag != tag: c = c.parent
        if c is not self.root: self.cur = c.parent
    def handle_data(self, d): self.cur.children.append(('text', d))
    def handle_entityref(self, name): self.cur.children.append(('text', f'&{name};'))
    def handle_charref(self, name): self.cur.children.append(('text', f'&#{name};'))

