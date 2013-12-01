def newline(tokens, ch):
    if ch == ' ':
        tokens.string += ch
        tokens.value  += 1
        return newline
    if ch == '\n':
        tokens.string += ch
        tokens.value   = 0
        return newline
    if ch == '#':
        tokens.string += ch
        tokens.value   = 0
        return comment
    current = tokens.indent[-1]
    if current < tokens.value:
        tokens.indent.append(tokens.value)
        tokens.push('indent')
    else:
        while tokens.indent[-1] > tokens.value:
            tokens.indent.pop(-1)
            tokens.push('dedent', False)
        if tokens.indent[-1] != tokens.value:
            raise Exception("broken dedent")
        if ch != '':
            tokens.push('newline')
    return idle(tokens, ch)

def comment(tokens, ch):
    tokens.string += ch
    if ch == '\n':
        tokens.value = 0
        return newline
    else:
        return comment

def identifier(tokens, ch):
    if ch.isalnum() or ch == '_':
        tokens.string += ch
        return identifier
    else:
        tokens.push('ident')
        if tokens.rich_depth > 0:
            tokens.string += ch
            return rich_string
        return idle(tokens, ch)

def number(tokens, ch):
    if ch.isdigit():
        tokens.string += ch
        return number
    else:
        tokens.push('number')
        return idle(tokens, ch)

def string_flush(tokens):
    if len(tokens.string) > 0:
        tokens.push('string_data')

def cheap_string(tokens, ch):
    if ch == "'":
        string_flush(tokens)
        tokens.string += ch
        tokens.push('string_end')
        return idle
    if ch == '\\':
        string_flush(tokens)
        tokens.string += ch
        return cheap_escape
    tokens.string += ch
    return cheap_string

def cheap_escape(tokens, ch):
    tokens.string += ch
    tokens.push('string_escape')
    return cheap_string

def rich_string(tokens, ch):
    if ch == '"':
        string_flush(tokens)
        tokens.string += ch
        tokens.push('string_end')
        tokens.rich_depth -= 1
        return idle
    if ch == '\\':
        string_flush(tokens)
        tokens.string += ch
        return rich_escape
    if ch == '$':
        return rich_dollar
    tokens.string += ch
    return rich_string

def rich_escape(tokens, ch):
    tokens.string += ch
    tokens.push('string_escape')
    return rich_string

def rich_dollar(tokens, ch):
    if ch == '{':
        string_flush(tokens)
        return idle
    if ch.isalpha() or ch == '_':
        string_flush(tokens)
        tokens.string += ch
        return identifier
    tokens.string += '$' + ch
    return rich_string


def idle(tokens, ch, mode=None):
    tokens.start = tokens.stop
    if ch.isalpha() or ch == '_':
        tokens.string += ch
        return identifier
    if ch.isdigit():
        tokens.string += ch
        return number
    if ch == '#':
        tokens.string += ch
        return comment
    if ch == '\n':
        tokens.string += ch
        return newline
    if ch == ' ':
        tokens.near = False
        return idle if mode is None else mode
    if ch == '':
        return None
    if ch == '"':
        tokens.string += ch
        tokens.push('string_begin')
        tokens.rich_depth += 1
        return rich_string
    if ch == "'":
        tokens.string += ch
        tokens.push('string_begin')
        return cheap_string
    if tokens.rich_depth > 0 and ch == "}":
        return rich_string
    tokens.string += ch
    tokens.push('symbol', offset=1)
    return idle if mode is None else mode

class TokenBuffer(object):
    def __init__(self):
        self.start = 0
        self.stop  = 0
        self.tokens = []
        self.string = ''
        self.value  = 0
        self.indent = [0]
        self.rich_depth = 0
        self.near = True

    def push(self, which, flush=True, offset=0):
        self.tokens.append(Token(which, self.string, self.near, self.start, self.stop+offset))
        self.near = True
        if flush:
            self.value = 0
            self.string = ''

class Token(object):
    def __init__(self, which, string, near, start, stop):
        self.which  = which
        self.string = string
        self.near  = near
        self.start = start
        self.stop  = stop

    def __repr__(self):
        return "%c%s(%r)@[%i:%i]" % ('+-'[self.near], self.which, self.string, self.start, self.stop)

def tokenize(source):
    tokens = TokenBuffer()
    index  = 0
    mode   = idle
    for index, ch in enumerate(source):
        tokens.stop = index
        mode = mode(tokens, ch)
    tokens.stop = index + 1
    mode(tokens, '')
    while tokens.indent[-1] > 0:
        tokens.indent.pop(-1)
        tokens.push('dedent', False)
    return tokens.tokens

def tokenize_file(path):
    with open(path) as fd:
        source = fd.read()
    return tokenize(source)

if __name__=="__main__":
    print tokenize(r"hello 'wo\nrld'\n  " + r'fo$+- *o "b\ar${2}and $buux"')
