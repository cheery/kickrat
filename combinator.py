import tokenizer

class result(object):
    def __init__(self, mark, values=None):
        self.mark = mark
        self.values = [] if values is None else values
        self.start = None
        self.stop  = None
    def __getitem__(self, index):
        return self.values[index]
    def __len__(self):
        return len(self.values)
    def __iter__(self):
        return iter(self.values)
    def __repr__(self):
        return "%s%r" % (self.mark, self.values)
    def append(self, value):
        self.values.append(value)
    @property
    def string(self):
        return ''.join(value.string for value in self)

class expect(object):
    def __init__(self, pos, terminals):
        self.terminals = set(terminals)
        self.pos = pos

    def __add__(self, other):
        if other is None:
            return self
        if self.pos < other.pos:
            return other
        if self.pos > other.pos:
            return self
        return expect(self.pos, self.terminals | other.terminals)

    def __lshift__(self, other):
        if other is None:
            return self
        if other.pos <= self.pos:
            return self
        else:
            return other

    def __repr__(self):
        return ' or '.join(str(o) for o in self.terminals)

def getpos(source, index):
    if index < len(source):
        return source[index].start
    if len(source) > 0:
        return source[len(source)-1].stop
    else:
        return 0

class label(object):
    def __init__(self, name):
        self.name = name
        self.link = None

    def match(self, source, index):
        return match(self.link, source, index)

class near(object):
    def __init__(self, subject):
        self.subject = subject

    def match(self, source, index):
        if index < len(source):
            if not source[index].near:
                i = source[index].start
                return -1, None
        return match(self.subject, source, index)


class choice(object):
    def __init__(self, *choices):
        self.choices = list(choices)
        self.name = None

    def append(self, choice):
        self.choices.append(choice)

    def match(self, source, index):
        ex = expect(getpos(source, index), [])
        for obj in self.choices:
            k, r = match(obj, source, index)
            if k >= 0:
                return k, r
            else:
                ex = ex + r
        if self.name:
            ex = expect(getpos(source, index), [self.name]) << ex
        return -1, ex

class star(object):
    def __init__(self, subject):
        self.subject = subject
        self.mark = self

    def match(self, source, index):
        count = 0
        res = result(self.mark)
        k, r = match(self.subject, source, index+count)
        while k >= 0:
            res.append(r)
            count += k
            k, r = match(self.subject, source, index+count)
        if count > 0:
            res.start = source[index].start
            res.stop  = source[index+count-1].stop
        return count, res

    def __repr__(self):
        return 'star%x' % id(self)

class plus(object):
    def __init__(self, subject):
        self.subject = subject
        self.mark = self

    def match(self, source, index):
        count = 0
        res = result(self.mark)
        k, r = match(self.subject, source, index+count)
        if k < 0:
            return -1, r
        while k >= 0:
            res.append(r)
            count += k
            k, r = match(self.subject, source, index+count)
        res.start = source[index].start
        res.stop  = source[index+count-1].stop
        return count, res

    def __repr__(self):
        return 'plus%x' % id(self)

class sequence(object):
    def __init__(self, *objects):
        self.objects = objects
        self.mark = self
        self.name = None

    def match(self, source, index):
        count = 0
        res = result(self.mark)
        for obj in self.objects:
            k, r = match(obj, source, index+count)
            if k >= 0:
                res.append(r)
                count += k
            elif self.name:
                return -1, expect(getpos(source, index), [self.name]) << r
            else:
                return -1, r
        res.start = source[index].start
        res.stop  = source[index+count-1].stop
        return count, res

    def __repr__(self):
        return 'sequence%x' % id(self)

class lookahead(object):
    def __init__(self, subject, positive=True):
        self.subject = subject
        self.positive = positive

    def match(self, source, index):
        k, res = match(self.subject, source, index)
        if self.positive:
            if k >= 0:
                return 0, res
            else:
                return -1, res
        else:
            if k < 0:
                return 0, res
            else:
                return -1, None

class optional(object):
    def __init__(self, subject):
        self.subject = subject

    def match(self, source, index):
        k, res = match(self.subject, source, index)
        if k >= 0:
            return k, res
        return 0, None

eof = object()

def match_string(string, source, index):
    if index < len(source):
        if source[index].string == string:
            return 1, source[index]
    return -1, expect(getpos(source, index), [repr(string)])

def match(obj, source, index):
    if isinstance(obj, (str, unicode)):
        return match_string(obj, source, index)
    if obj is eof:
        if len(source) == index:
            return 0, None
        else:
            return -1, expect(getpos(source, index), ['eof'])
    return obj.match(source, index)

def parse(root, source):
    tokens = tokenizer.tokenize(source)
    return match(root, tokens, 0)
