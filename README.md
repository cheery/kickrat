# Kickrat

Kickrat is a parser generator meant for writing indentation sensitive programming languages.

It consists of:

 * A small state-based tokenizer uniform enough for many languages
 * A set of PEG-combinators, that are used to describe the language in python.

Parsing expression grammars let you describe the syntax rules that are recognised as the language. Each of the combinators given have simple operation:

 * `choice(pattern, ...)` matches the first pattern that matches.
 * `sequence(pattern, ...)` matches sequence of patterns.
 * `star(pattern)` matches zero or more patterns.
 * `plus(pattern)` matches one or more patterns.
 * `near(pattern)` matches pattern that is not separated by space from the earlier pattern.

Aside these combinators you need several patterns that match to input tokens. They are called terminals. You have following terminals:

 * `Regex('regex-string')` matches token strings that match the regex.
 * `ident`, `number`, `indent`, `newline`, `dedent`, `string_begin`, `string_data`, `string_escape`, `string_end` matches tokens of those types.
 * bare strings match to complete strings within tokens.

Because the choice always recognises the first pattern that matches, parsing expression grammars are unambigous. It also means that it's easy to introduce new rules into the grammar. This makes it easy to make the parser recognise only the patterns that the language implementation can handle.

## Shortcomings

Kickrat doesn't have error handling, and it doesn't handle indentation intermixed with parentheses. You only get 'syntax error'.

Generated parser doesn't recognise left-recursive grammars, so it will hang into them. Though that doesn't remove any expressive power. Instead of typing `expr20 = sequence(expr20, '+', expr30)`, just type: `expr20 = sequence(expr30, plus('+' expr30))` and it works just as well.

Parser are also unoptimized and likely very slow at parsing.

Written in python2.7, might have trouble porting to python3.

## Example

    from kickrat import *
    import operator

    optable = {
        '+': operator.add,
        '-': operator.sub,
        '*': operator.mul,
        '/': operator.div,
    }

    def calculate(node):
        lhs = node[0].mark(node[0])
        for op, rhs in node[1]:
            rhs = rhs.mark(rhs)
            lhs = optable[op.string](lhs, rhs)
        return lhs

    def operators(prev, *operators):
        op = sequence(prev, plus(sequence(choice(*operators), prev)))
        op.mark = calculate
        return choice(op, prev)

    l_expr = label('expr')

    number_float = sequence(number, '.', number)
    number_float.mark = lambda node: float(node.string)

    number16 = sequence(number, near(Regex('^x[0-9a-fA-F]+$')))
    number16.mark = lambda node: int(node.string, 16)

    number10 = sequence(number)
    number10.mark = lambda node: int(node.string, 10)

    parens = sequence('(', l_expr, ')')
    parens.mark = lambda node: node[1].mark(node[1])

    term = choice(
        number_float,
        number16,
        number10,
        parens
    )

    expr = term
    expr = operators(expr, '*', '/')
    expr = operators(expr, '+', '-')
    l_expr.link = expr

    try:
        expr = sequence(expr, eof)
        while True:
            source = raw_input("ratmeat> ")
            k, res = parse(expr, source)
            if k >= 0:
                print res[0].mark(res[0])
            else:
                print "syntax error"
    except (KeyboardInterrupt, EOFError) as e:
        print

## Links

 * [The Packrat Parsing and 
Parsing Expression Grammars Page](http://bford.info/packrat/)
