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
                return -1, None
        return match(self.subject, source, index)


class choice(object):
    def __init__(self, *choices):
        self.choices = list(choices)

    def append(self, choice):
        self.choices.append(choice)

    def match(self, source, index):
        for obj in self.choices:
            k, r = match(obj, source, index)
            if k >= 0:
                return k, r
        return -1, None

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
            return -1, None
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

    def match(self, source, index):
        count = 0
        res = result(self.mark)
        for obj in self.objects:
            k, r = match(obj, source, index+count)
            if k >= 0:
                res.append(r)
                count += k
            else:
                return -1, None
        res.start = source[index].start
        res.stop  = source[index+count-1].stop
        return count, res

    def __repr__(self):
        return 'sequence%x' % id(self)

eof = object()

def match_string(string, source, index):
    if index < len(source):
        if source[index].string == string:
            return 1, source[index]
    return -1, None

def match(obj, source, index):
    if isinstance(obj, (str, unicode)):
        return match_string(obj, source, index)
    if obj is eof:
        if len(source) == index:
            return 0, None
        else:
            return -1, None
    return obj.match(source, index)

def parse(root, source):
    tokens = tokenizer.tokenize(source)
    return match(root, tokens, 0)
