class Output(object):
    start = None
    stop  = None

class List(Output):
    def __init__(self, name=None, values=None):
        self.name = name
        self.values = [] if values is None else values

    def __repr__(self):
        if self.name is None:
            return repr(self.values)
        return "%s%r" % (self.name, self.values)

    @property
    def string(self):
        return ''.join(value.string for value in self.values)

    def __getitem__(self, index):
        return self.values[index]

    def __iter__(self):
        return iter(self.values)

    def __len__(self):
        return len(self.values)

    def include(self, node):
        if node.name is not None:
            self.values.append(node)
        elif isinstance(node, List):
            self.values.extend(node)

class String(Output):
    def __init__(self, name, string):
        self.name   = name
        self.string = string

    def __repr__(self):
        if self.name is None:
            return repr(self.string)
        return "%s%r" % (self.name, self.string)
