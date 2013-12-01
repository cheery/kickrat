class Backtrack(Exception):
    pass

class Stream(object):
    def __init__(self, tokens):
        self.tokens = tokens
        self.cache  = [{} for i in range(len(tokens) + 1)]
        self.pos    = 0

        self.extreme  = 0
        self.failures = set()

    @property
    def eof(self):
        return self.pos >= len(self.tokens)

    def get(self, pos):
        if 0 <= pos < len(self.tokens):
            return self.tokens[pos]

    def fail(self, pos, message):
        if self.extreme > pos:
            self.extreme = pos
            self.failures.clear()
        if self.extreme == pos:
            self.failures.add(message)

    def intro(self, pattern):
        memo = self.cache[self.pos]
        if pattern not in memo:
            memo[pattern] = None, self.pos
            return False
        return True

    def fetch(self, pattern):
        output, self.pos = self.cache[self.pos][pattern]
        if output is None:
            raise Backtrack
        return output

    def store(self, pattern, pos, output):
        memo = self.cache[pos]
        endpos = self.pos
        output.start = self.get(pos).start
        output.stop  = self.get(endpos-1).stop
        if pattern.recursive:
            try:
                while True:
                    self.pos = pos
                    output = pattern.force(self, pattern, (output, endpos))
                    endpos = self.pos
            except Backtrack:
                self.pos = endpos
        memo[pattern] = output, endpos
        return output

    def plant(self, seed):
        self.pos = seed[1]
        return seed[0]

    def expected(self, pos, string):
        self.fail(pos, "%s expected" % string)
        raise Backtrack
