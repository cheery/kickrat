# Kickrat

Kickrat is a parser generator meant for writing indentation sensitive programming languages.

It consists of:

 * A small state-based tokenizer uniform enough for many languages
 * A set of PEG-combinators, that are used to describe the language in python.

The following instructions are slightly out of date. Peek inside examples to see working code. I propose you to check into different libraries if you want for stable, working system without surprises.

Parsing expression grammars let you describe the syntax rules that are recognised as the language. Each of the combinators given have simple operation:

 * `choice(pattern, ...)` matches the first pattern that matches.
 * `sequence(pattern, ...)` matches sequence of patterns.
 * `many(pattern)` matches zero or more patterns.
 * `plus(pattern)` matches one or more patterns.
 * `near(pattern)` matches pattern that is not separated by space from the earlier pattern.
 * `opt(pattern)` matches anyway, but if pattern matches, it grabs it.

Aside these combinators you need several patterns that match to input tokens. They are called terminals. You have following terminals:

 * `ident`, `number`, `indent`, `newline`, `dedent`, `string_begin`, `string_data`, `string_escape`, `string_end` matches tokens of those types.
 * bare strings match to complete strings within tokens.

Because the choice always recognises the first pattern that matches, parsing expression grammars are unambigous. It also means that it's easy to introduce new rules into the grammar. This makes it easy to make the parser recognise only the patterns that the language implementation can handle.

## Shortcomings

Kickrat doesn't have error handling, and it doesn't handle indentation intermixed with parentheses. You only get 'syntax error'.

Parser are slightly unoptimized and likely very slow at parsing.

Written in python2.7, might have trouble porting to python3.

## Links

 * [The Packrat Parsing and 
Parsing Expression Grammars Page](http://bford.info/packrat/)
