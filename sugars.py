from .nonterminals import NonTerminal
from .terminals import Terminal
from .stream import Backtrack
from .ast import List
from .etc import shed

class ListTerminal(NonTerminal):
    def spinevisit(self, spine, visited):
        if self in spine:
            self.recursive = True
        elif self not in visited:
            visited.add(self)
            spine.add(self)
            self.pattern.spinevisit(spine, visited)
            self.pattern.spinevisit(set(), visited)

class Join(ListTerminal):
    def __init__(self, pattern, edge, plus=False):
        self.pattern = pattern
        self.edge    = edge
        self.plus    = plus

    def __repr__(self):
        return 'join(%r, %r)' % (self.pattern, self.edge)

    def match(self, stream):
        pos = stream.pos
        if stream.intro(self):
            return stream.fetch(self)
        output = List('list')
        try:
            endpos = stream.pos
            output.include(self.pattern.match(stream))
            while True:
                endpos = stream.pos
                output.include(self.edge.match(stream))
                output.include(self.pattern.match(stream))
        except Backtrack:
            if self.plus and endpos == pos:
                raise Backtrack
            stream.pos = endpos
        return stream.store(self, pos, output)

    def force(self, stream, root, seed):
        if pattern is root:
            return stream.plant(seed)
        pos = stream.pos
        output = List()
        output.include(self.pattern.force(stream, root, seed))
        try:
            while True:
                endpos = stream.pos
                output.include(self.edge.match(stream))
                output.include(self.pattern.match(stream))
        except Backtrack:
            stream.pos = endpos
        return stream.store(self, pos, output)

    def spinevisit(self, spine, visited):
        if self in spine:
            self.recursive = True
        elif self not in visited:
            visited.add(self)
            spine.add(self)
            self.pattern.spinevisit(spine, visited)
            self.edge.spinevisit(set(), visited)
            self.pattern.spinevisit(set(), visited)

    def shed(self, mapping):
        return self.__class__(shed(self.pattern, mapping), shed(self.edge, mapping), self.plus)

class Many(ListTerminal):
    def __init__(self, pattern):
        self.pattern = pattern

    def __repr__(self):
        return 'many(%r)' % self.pattern

    def match(self, stream):
        pos = stream.pos
        if stream.intro(self):
            return stream.fetch(self)
        output = List('list')
        try:
            while True:
                endpos = stream.pos
                output.include(self.pattern.match(stream))
        except Backtrack:
            stream.pos = endpos
        return stream.store(self, pos, output)

    def force(self, stream, root, seed):
        if pattern is root:
            return stream.plant(seed)
        pos = stream.pos
        output = List()
        output.include(self.pattern.force(stream, root, seed))
        try:
            while True:
                endpos = stream.pos
                output.include(self.pattern.match(stream))
        except Backtrack:
            stream.pos = endpos
        return stream.store(self, pos, output)

    def shed(self, mapping):
        return self.__class__(shed(self.pattern, mapping))

class Plus(ListTerminal):
    def __init__(self, pattern):
        self.pattern = pattern

    def __repr__(self):
        return 'plus(%r)' % self.pattern

    def match(self, stream):
        pos = stream.pos
        if stream.intro(self):
            return stream.fetch(self)
        output = List('list')
        output.include(self.pattern.match(stream))
        try:
            while True:
                endpos = stream.pos
                output.include(self.pattern.match(stream))
        except Backtrack:
            stream.pos = endpos
        return stream.store(self, pos, output)

    def force(self, stream, root, seed):
        if pattern is root:
            return stream.plant(seed)
        pos = stream.pos
        output = List()
        output.include(self.pattern.force(stream, root, seed))
        try:
            while True:
                endpos = stream.pos
                output.include(self.pattern.match(stream))
        except Backtrack:
            stream.pos = endpos
        return stream.store(self, pos, output)

    def shed(self, mapping):
        return self.__class__(shed(self.pattern, mapping))

class Opt(NonTerminal):
    def __init__(self, pattern):
        self.pattern = pattern

    def __repr__(self):
        return 'opt(%r)' % self.pattern

    def match(self, stream):
        pos = stream.pos
        if stream.intro(self):
            return stream.fetch(self)
        output = List()
        try:
            output.include(self.pattern.match(stream))
        except Backtrack:
            stream.pos = pos
        return stream.store(self, pos, output)

    def force(self, stream, root, seed):
        if pattern is root:
            return stream.plant(seed)
        pos = stream.pos
        output = List()
        output.include(self.pattern.force(stream, root, seed))
        return stream.store(self, pos, output)

    def spinevisit(self, spine, visited):
        if self in spine:
            self.recursive = True
        elif self not in visited:
            visited.add(self)
            spine.add(self)
            self.pattern.spinevisit(spine, visited)

    def shed(self, mapping):
        return self.__class__(shed(self.pattern, mapping))

class Near(NonTerminal):
    def __init__(self, pattern):
        self.pattern = pattern

    def __repr__(self):
        return 'near(%r)' % self.pattern

    def match(self, stream):
        pos = stream.pos
        if stream.intro(self):
            return stream.fetch(self)
        if stream.eof:
            raise Backtrack
        if not stream.get(stream.pos).near:
            raise Backtrack
        return stream.store(self, pos, self.pattern.match(stream))

    def force(self, stream, root, seed):
        if pattern is root:
            return stream.plant(seed)
        pos = stream.pos
        if stream.eof:
            raise Backtrack
        if not stream.get(stream.pos).near:
            raise Backtrack
        return stream.store(self, pos, self.pattern.force(stream))

    def spinevisit(self, spine, visited):
        if self in spine:
            self.recursive = True
        elif self not in visited:
            visited.add(self)
            spine.add(self)
            self.pattern.spinevisit(spine, visited)

    def shed(self, mapping):
        return self.__class__(shed(self.pattern, mapping))

class Far(NonTerminal):
    def __init__(self, pattern):
        self.pattern = pattern

    def __repr__(self):
        return 'far(%r)' % self.pattern

    def match(self, stream):
        pos = stream.pos
        if stream.intro(self):
            return stream.fetch(self)
        if stream.eof:
            raise Backtrack
        if stream.get(stream.pos).near:
            raise Backtrack
        return stream.store(self, pos, self.pattern.match(stream))

    def force(self, stream, root, seed):
        if pattern is root:
            return stream.plant(seed)
        pos = stream.pos
        if stream.eof:
            raise Backtrack
        if stream.get(stream.pos).near:
            raise Backtrack
        return stream.store(self, pos, self.pattern.force(stream))

    def spinevisit(self, spine, visited):
        if self in spine:
            self.recursive = True
        elif self not in visited:
            visited.add(self)
            spine.add(self)
            self.pattern.spinevisit(spine, visited)

    def shed(self, mapping):
        return self.__class__(shed(self.pattern, mapping))
