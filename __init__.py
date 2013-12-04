from .tokenizer import tokenize, tokenize_file
from .stream import Backtrack, Stream
from .ast import List, String
from .terminals import TokenTerminal, StringTerminal
from .nonterminals import NonTerminal, Choice, Sequence
from .sugars import Join, Many, Plus, Opt, Near, Far
from .etc import shed

class HeapSlice(object):
    def __init__(self, heap, idx):
        self.heap = heap
        self.idx  = idx
        self.patterns = None

    def slot(self, priority, pattern):
        if isinstance(self.idx, slice):
            start = self.idx.start 
            stop  = self.idx.stop
            if start is None:
                start = priority
            if stop is None:
                stop = priority + 1
            if start <= priority < stop:
                self.patterns.append(pattern)
        elif priority == self.idx:
            self.patterns.append(pattern)

    def shed(self, mapping):
        if self in mapping:
            return mapping[self]
        shed(self.heap, mapping)
        out = mapping[self] = Choice(self.patterns)
        return out

class PriorityHeap(object):
    def __init__(self):
        self.patterns = []
        self.slicecache = {}

    def __call__(self, priority, *patterns):
        for pattern in patterns:
            self.patterns.append((priority, pattern))

    def define(self, priority, *patterns):
        for pattern in patterns:
            self.patterns.append((priority, pattern))

    def __getitem__(self, idx):
        if isinstance(idx, slice):
            key = ('slice', idx.start, idx.stop)
        else:
            key = idx
        if key in self.slicecache:
            return self.slicecache[key]
        self.slicecache[key] = res = HeapSlice(self, idx)
        return res

    def shed(self, mapping):
        self.patterns.sort(key=lambda x: -x[0])
        slots = []
        for item in self.slicecache.values():
            item.patterns = []
            slots.append(item)
        patterns = []
        out = mapping[self] = Choice(patterns)
        for priority, pattern in self.patterns:
            pattern = shed(pattern, mapping)
            patterns.append(pattern)
            for slot in slots:
                slot.slot(priority, pattern)
        return out

class Grammar(object):
    def __init__(self, pattern):
        self.pattern = shed(pattern, {})
        self.pattern.spinevisit(set(), set())
        print self.pattern

    def parse(self, source):
        return parse(self.pattern, source)

def declare():
    return PriorityHeap()

# fix this stuff later...
def print_error(stream, source):
    current = stream.get(stream.extreme)
    pos = len(source) if current is None else current.start
    print ', '.join(stream.failures), 'at %i' % pos

def parse(pattern, source):
    stream = Stream(tokenize(source))
    try:
        output = pattern.match(stream)
        if not stream.eof:
            print_error(stream, source)
        return output
    except Backtrack:
        print_error(stream, source)


def sequence(*patterns, **kw):
    name = kw.get('name')
    if len(patterns) == 1 and not name:
        return patterns[0]
    else:
        return Sequence(patterns, name)

def choice(*patterns):
    return Choice(patterns)

def many(*patterns, **kw):
    return Many(sequence(*patterns, **kw))

def plus(*patterns, **kw):
    return Plus(sequence(*patterns, **kw))

def opt(*patterns, **kw):
    return Opt(sequence(*patterns, **kw))

def near(*patterns, **kw):
    return Near(sequence(*patterns, **kw))

def far(*patterns, **kw):
    return Far(sequence(*patterns, **kw))

#def lookahead(*patterns):
#    if len(patterns) == 1:
#        return Lookahead(build(patterns[0]))
#    else:
#        return Lookahead(Sequence(map(build, patterns)))
#
#def no(*patterns):
#    if len(patterns) == 1:
#        return NegativeLookahead(build(patterns[0]))
#    else:
#        return NegativeLookahead(Sequence(map(build, patterns)))
#
##class Regex(object):
##    def __init__(self, string, flags=0):
##        self.pattern = re.compile(string, flags)
##
##    def match(self, source, index):
##        if index < len(source):
##            match = self.pattern.match(source[index].string)
##            if match is not None:
##                return 1, source[index]
##        return -1, None
##
ident  = TokenTerminal('ident')
number = TokenTerminal('number')
symbol = TokenTerminal('symbol')

indent  = TokenTerminal('indent', False)
newline = TokenTerminal('newline', False)
dedent  = TokenTerminal('dedent', False)

string_begin  = TokenTerminal('string_begin', False)
string_data   = TokenTerminal('string_data')
string_escape = TokenTerminal('string_escape', False)
string_end    = TokenTerminal('string_end')
#
#def parse_file(pattern, path):
#    with open(path, 'r') as fd:
#        source = fd.read()
#    return parse(pattern, source)
