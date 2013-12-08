from .. import *

expr = declare()
expr(0, number)
expr(0, sequence('-', number, name="neg"))
expr(0, sequence('(', expr, ')'))
expr(1,
    sequence(expr[:2], '*', expr[:1], name="mul"),
    sequence(expr[:2], '/', expr[:1], name="div"),
)
expr(2,
    sequence(expr[:3], '+', expr[:2], name="add"),
    sequence(expr[:3], '-', expr[:2], name="sub"),
)

def calc(data):
    if data.name == 'number':
        return int(data.string)
    if data.name == 'neg':
        return -calc(data[0])
    if data.name == 'mul':
        lhs, rhs = data
        return calc(lhs) * calc(rhs)
    if data.name == 'div':
        lhs, rhs = data
        return calc(lhs) / calc(rhs)
    if data.name == 'add':
        lhs, rhs = data
        return calc(lhs) + calc(rhs)
    if data.name == 'sub':
        lhs, rhs = data
        return calc(lhs) - calc(rhs)

if __name__=='__main__':
    grammar = Grammar(expr)
    while True:
        string = raw_input('> ')
        output = grammar.parse(string)
        if output is not None:
            print calc(output)
