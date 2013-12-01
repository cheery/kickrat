from .terminals import Terminal
from .stream import Backtrack
from .ast import List
from .etc import shed

class NonTerminal(object):
    recursive = False

class Choice(NonTerminal):
    def __init__(self, patterns):
        self.patterns = patterns

    def __repr__(self):
        return 'choice%r' % (self.patterns,)

    def __getitem__(self, index):
        return self.patterns[index]

    def __iter__(self):
        return iter(self.patterns)

    def match(self, stream):
        if stream.intro(self):
            return stream.fetch(self)
        pos = stream.pos
        for pattern in self:
            try:
                return stream.store(self, pos, pattern.match(stream))
            except Backtrack:
                stream.pos = pos
        raise Backtrack

    def force(self, stream, root, seed):
        pos = stream.pos
        for pattern in self:
            if pattern is root:
                return stream.plant(seed)
            if isinstance(pattern, Terminal):
                continue
            try:
                return stream.store(self, pos, pattern.force(stream, root, seed))
            except Backtrack:
                stream.pos = pos
        raise Backtrack

    def spinevisit(self, spine, visited):
        if self in spine:
            self.recursive = True
        elif self not in visited:
            visited.add(self)
            spine.add(self)
            for pattern in self:
                pattern.spinevisit(spine.copy(), visited)

    def shed(self, mapping):
        return self.__class__([shed(pat, mapping) for pat in self])

class Sequence(NonTerminal):
    def __init__(self, patterns, name=None):
        self.patterns = patterns
        self.name = name

    def __repr__(self):
        return 'sequence%r' % (self.patterns,)

    def __getitem__(self, index):
        return self.patterns[index]

    def __iter__(self):
        return iter(self.patterns)

    def match(self, stream):
        pos = stream.pos
        if stream.intro(self):
            return stream.fetch(self)
        output = List(self.name)
        for pattern in self:
            output.include(pattern.match(stream))
        return stream.store(self, pos, output)

    def force(self, stream, root, seed):
        pos = stream.pos
        patterns = iter(self)
        first = patterns.next()
        output = List(self.name)
        if first is root:
            output.include(stream.plant(seed))
        else:
            output.include(first.force(stream, root, seed))
        for pattern in patterns:
            output.include(pattern.match(stream))
        return stream.store(self, pos, output)

    def spinevisit(self, spine, visited):
        if self in spine:
            self.recursive = True
        elif self not in visited:
            visited.add(self)
            spine.add(self)
            patterns = iter(self)
            patterns.next().spinevisit(spine, visited)
            for pattern in patterns:
                pattern.spinevisit(set(), visited)

    def shed(self, mapping):
        return self.__class__([shed(pat, mapping) for pat in self], self.name)
