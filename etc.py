from .terminals import StringTerminal

def shed(obj, mapping):
    if obj in mapping:
        return mapping[obj]
    if isinstance(obj, basestring):
        out = StringTerminal(obj)
    else:
        out = obj.shed(mapping)
    mapping[obj] = out
    return out
