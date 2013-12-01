from .ast import List, String
from .stream import Backtrack

class Terminal(object):
    recursive = False

    def force(self, stream, root, seed):
        raise Backtrack

    def spinevisit(self, spine, visited):
        pass

    def shed(self, mapping):
        return self

class TokenTerminal(Terminal):
    def __init__(self, which, ignore=False):
        self.which = which
        self.ignore = ignore

    def __repr__(self):
        return 'which==%r' % self.which

    def match(self, stream):
        pos = stream.pos
        current = stream.get(pos)
        if not stream.eof and current.which == self.which:
            name = None if self.ignore else self.which
            output = String(name, current.string)
            stream.pos += 1
            return stream.store(self, pos, output)
        else:
            stream.expected(pos, self.which)

class StringTerminal(Terminal):
    def __init__(self, string):
        self.string = string

    def __repr__(self):
        return 'string==%r' % self.string

    def match(self, stream):
        pos = stream.pos
        string = ''
        length = len(self.string)
        index = pos
        while len(string) < length:
            if stream.eof:
                stream.expected(pos, repr(self.string))
            current = stream.get(index)
            string += current.string
            if pos < index and not current.near:
                stream.expected(pos, repr(self.string))
            if not self.string.startswith(string):
                stream.expected(pos, repr(self.string))
            index += 1
        stream.pos = index
        return stream.store(self, pos, String(None, string))
