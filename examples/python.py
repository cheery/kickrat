from .. import *
from os.path import dirname, join
path = join(dirname(dirname(__file__)), 'tokenizer.py')

# in it's current state, this code parses only some of python. It's not enough to parse entire tokenizer.py file though.

term       = declare()
expression = declare()
statement  = declare()

term.define(0,
    sequence('-', term, name='neg'),
    sequence(term, '[', expression, ']', name="item"),
    sequence(term, '.', near(ident), name="attr"),
    sequence('False', name="False"),
    sequence('True', name="True"),
    ident,
    number,
    sequence(string_begin, many(choice(string_data, string_escape)), string_end, name='string'),
)

expression.define(50,
    sequence(expression, '(', Join(expression, ','), ')', name="call"),
    sequence(term, '==', expression, name='=='),
    sequence(term, '!=', expression, name='!='),
    sequence(term, '<', expression, name='<'),
    sequence(term, '>', expression, name='>'),
)
expression.define(0, term)

variable = declare()
variable.define(0,
    sequence(variable, '.', near(ident), name="attr"),
    ident,
)

arglist = Join(ident, ',')
statements = Join(statement, newline, plus=True)
statement.define(50,
    sequence('def', ident, '(', arglist, ')', ':',
        indent,
        statements,
        opt(dedent),
    name="def"),
    sequence('if', expression, ':',
        indent, statements, opt(dedent),
        opt(newline, 'else', ':', indent, statements, opt(dedent), name='else'),
    name='if'),
    sequence('while', expression, ':',
        indent, statements, dedent,
    name='while'),
    sequence('raise', expression, name="raise"),
    sequence('return', expression, name="return"),
    sequence(variable, '+=', expression, name="+="),
    sequence(variable, '=',  expression, name="="),
    expression,
)

#term.define(sequence(term, '.', near(ident)).prune(0, 2, name='attr'))
#term.define(sequence(term, '[', expression, ']').prune(0, 2, name='item'))
#term.define(sequence(no('def'), no('return'), no('if'), no('else'), ident).prune(2, name='identifier'))
#term.define(sequence(
#    string_begin, star(choice(
#        string_data,
#        string_escape,
#    )), string_end
#).prune(1, name='string'))
#term.define(number.prune(name='number'))
#
#term.define(sequence('-', term))
#
#expression_50 = choice(
#    sequence(term, '(', expression, star(',', expression), ')').prune(0, 2, name='call'),
#    sequence(term, '-', expression).prune(0, 2, name='-'),
#    sequence(term, '<', expression).prune(0, 2, name='<'),
#    sequence(term, '>', expression).prune(0, 2, name='>'),
#    sequence(term, '=', near('='), term).prune(0, 3, name='=='),
#    term,
#)
#
#expression.define(sequence(expression_50, '=', expression).prune(0, 2, name='='))
#expression.define(
#    sequence(term, '+', near('='), expression).prune(0, 3, name='+=')
#)
#expression.define(expression_50)
#expression.define(term)
#
#arglist = choice(
#    sequence('(', ident, star(',', ident).prune(1), optional(','), ')').prune(1, flatten=2),
#    sequence('(', ')')
#)
#
#statement_block = sequence(
#    indent, statement, star(newline, statement).prune(1), dedent,
#).prune(1, flatten=2)
#
#statement.define(sequence('def', ident, arglist, ':',
#        statement_block,
#).prune(1, 2, 4, name='def'), priority=10)
#
#statement.define(sequence('if', expression, ':',
#    statement_block,
#    optional('else', ':', statement_block),
#).prune(1, 3, name='if'))
#
#statement.define(sequence('else', ':', statement_block))
#
#statement.define(sequence('return', expression).prune(1, name='return'))
#
#statement.define(expression)
#
#grammar = statement

def main():
    grammar = Grammar(statements)
    with open(path) as fd:
        source = fd.read()
    output = grammar.parse(source)
    print output
#    stream = parse_file(grammar, path)
#    print stream
#    print stream.eof
#
#    print stream.failures
#    print stream.tokens[stream.extreme:stream.extreme+10]
#    print stream.tokens[stream.pos:stream.pos+10]

if __name__=='__main__':
    main()
    #import cProfile
    #cProfile.run('main()')
