from kickrat.combinator import label, choice, star, plus, sequence, lookahead, optional, parse, near, eof
from kickrat.tokenizer import tokenize
import re

class TokenMatch(object):
    def __init__(self, which):
        self.which = which

    def match(self, source, index):
        if index < len(source):
            if source[index].which == self.which:
                return 1, source[index]
        return -1, None

class Regex(object):
    def __init__(self, string, flags=0):
        self.pattern = re.compile(string, flags)

    def match(self, source, index):
        if index < len(source):
            match = self.pattern.match(source[index].string)
            if match is not None:
                return 1, source[index]
        return -1, None

ident  = TokenMatch('ident')
number = TokenMatch('number')

indent  = TokenMatch('indent')
newline = TokenMatch('newline')
dedent  = TokenMatch('dedent')

string_begin  = TokenMatch('string_begin')
string_data   = TokenMatch('string_data')
string_escape = TokenMatch('string_escape')
string_end    = TokenMatch('string_end')

def parse_file(pattern, path):
    with open(path, 'r') as fd:
        source = fd.read()
    return parse(pattern, source)
