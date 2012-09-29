=========
rsonlite
=========

Version 0.1

Copyright (c) 2012, Patrick Maupin


.. contents::

Abstract
============

rsonlite is the easiest way to create custom indented data file
formats in Python.  It is a single small module that can be shipped
with your application, or it can be easy-installed or pipped from PyPI.

Background
=============

The `rson project`__ contains a parser that allows experimentation with
variations on readable file formats, and defines a base RSON profile that
is a strict superset of JSON (properly subclassed, the RSON parser passes
the Python simplejson testsuite, which itself creates a superset of JSON).


__ http://code.google.com/p/rson

RSON was born out of frustration with the size and speed of the available
pure-Python YAML parsers at the time, and was designed with very similar
goals to YAML -- key to these formats is the use of indentation as syntax,
removal of unnecessary syntactical elements such as quotes whenever possible,
the ability to add comments, and the ability to use JSON as valid input.

The base RSON format definition was designed to be easily parseable from any
language, but the Python parser itself is both flexible and fast, allowing
for variant formats to be easily designed and tested.  One such format is
something that `easily round-trips to XML`__ and another format allows
`macros and include processing`__.

__ http://code.google.com/p/rson/source/browse/trunk/tools/testxml.py
__ http://code.google.com/p/rson/source/browse/trunk/tools/rsonmac.py

But the flexibility comes at a price.  There is more code, and the learning curve
for all the options is more steep than it would be if the parser was not that
flexible, and the documentation -- well, it would take a long time to do a
decent job on properly documenting all the options, so that hasn't happened yet.

rsonlite is a pared-down version of rson that primarily handles the semantics
of the indentation, allowing client code to do higher-level parsing.  Unlike
JSON or base RSON, which distinguish between 'true', 'false', 'null', strings,
and numbers, or simplejson, which adds 'Nan' and 'Infinity' to the mix, rsonlite
divides the world up into container nodes and leaf nodes, and every leaf node is
a string.

Introduction
=============

rsonlite is a Python library that makes it easy to build a file
parser for declarative hierarchical data structures using indentation.
(Spaces only -- tabs are not considered indentation.)

Syntax
--------

The only special characters are **#**, **=**, and indentation:

  Indentation
    Indentation denotes a key/value relationship.  The
    value is indented from the key.

  =
    Denotes the start of a free-format string.  These
    strings can contain '=' and '#' characters, and
    even be multi-line, but every line in the string
    must be indented past the initial equal sign.

    Note that, for multi-line strings, indentation is
    preserved but normalized such that at least one
    line starts in the left column.  This allows for
    restructuredText or Python code, or even
    additional rsonlite to be parsed later, to exist
    inside multi-line strings.

  #
    Denotes the start of a line comment, when not
    inside a free-format string.

Objects
---------

The only Python objects resulting from parsing a file
with rsonlite.loads() are:

  strings
    free-format strings (described above) can
    contain any character, but the whitespace
    before/after the string may be stripped.

    Regular strings must fit on a single line and
    cannot contain '=' or '#' characters.

    Regular strings may be used as keys in key/value
    pairs, but free-format strings may not.

  tuple
    A key/value pair is a two-element tuple.  The key is always
    a string.  The value is always a list.  (It was judged
    that the consistency of always having the value be a list
    was more useful than the shortcut of simply letting the
    value sometimes be a single string.)

  list
    The top level is a list, and the value element of every
    key/value pair tuple is also a list.  Lists can contain
    strings and key/value pair tuples.

rsonlite.simpleparse() leverages rsonlite.loads to return a data
structure with dictionaries.  Ordered dictionaries are used if
they are available, otherwise standard dictionaries are used.

lists are returned whereever dictionaries would not work or
would lose information.

Exceptions
------------

As far as rsonlite is concerned, most input data is fine.
The main thing that makes it unhappy is indentation errors,
and it will throw the Python IndentationError exception if
it encounters an invalid indentation.

Examples
==========

I have shamelessly stolen most of these examples from the 
`JSON example page`__, because JSON is an excellent
thing to compare and contrast rsonlite against.

__ http://json.org/example.html

Example 1::

    >>> import rsonlite
    >>> jsonstr1 = '''
    ... {
    ...     "glossary": {
    ...         "title": "example glossary",
    ...         "GlossDiv": {
    ...             "title": "S",
    ...             "GlossList": {
    ...                 "GlossEntry": {
    ...                     "ID": "SGML",
    ...                     "SortAs": "SGML",
    ...                     "GlossTerm": "Standard Generalized Markup Language",
    ...                     "Acronym": "SGML",
    ...                     "Abbrev": "ISO 8879:1986",
    ...                     "GlossDef": {
    ...                         "para": "A meta-markup language",
    ...                         "GlossSeeAlso": ["GML", "XML"]
    ...                     },
    ...                     "GlossSee": "markup"
    ...                 }
    ...             }
    ...         }
    ...     }
    ... }
    ... '''
    >>>
    >>> rsonstr1 = '''
    ...     glossary
    ...         title = example glossary
    ...         GlossDiv
    ...             title = S
    ...             GlossList
    ...                 GlossEntry
    ...                     ID = SGML
    ...                     SortAs = SGML
    ...                     GlossTerm = Standard Generalized Markup Language
    ...                     Acronym = SGML
    ...                     Abbrev = ISO 8879:1986
    ...                     GlossDef
    ...                         para = A meta-markup language
    ...                         GlossSeeAlso = [GML, XML]
    ...                     GlossSee = markup
    ... '''
    >>>
    >>> jsondata1 = eval(jsonstr1)
    >>> rsondata1 = rsonlite.simpleparse(rsonstr1)
    >>> jsondata1 == rsondata1
    True

Example 2::

    >>> jsonstr2 = '''
    ... {"menu": {
    ...     "id": "file",
    ...     "value": "File",
    ...     "popup": {
    ...         "menuitem": [
    ...         {"value": "New", "onclick": "CreateNewDoc()"},
    ...         {"value": "Open", "onclick": "OpenDoc()"},
    ...         {"value": "Close", "onclick": "CloseDoc()"}
    ...         ]
    ...     }
    ... }}
    ... '''
    >>>
    >>> rsonstr2 = '''
    ...     menu
    ...         id = file
    ...         value = File
    ...         popup
    ...             menuitem
    ...                 value = New
    ...                 onclick = CreateNewDoc()
    ...                 value = Open
    ...                 onclick = OpenDoc()
    ...                 value = Close
    ...                 onclick = CloseDoc()
    ... '''
    >>>
    >>> jsondata2 = eval(jsonstr2)
    >>> rsondata2 = rsonlite.simpleparse(rsonstr2)
    >>> jsondata2 == rsondata2
    True

API
====

rsonlite.loads(source)
------------------------

This is the primary interface.  It returns a list of tuples,
strings, and lists, as defined in the introduction.

rsonlite.dumps(data, indent='    ', initial_indent='')
--------------------------------------------------------

This function takes data as returned from loads() and dumps it
back out to a string.  For example::

    >>> rsondata1 = rsonlite.loads(rsonstr1)
    >>> roundtrip = rsonlite.dumps(rsondata1, initial_indent='    ')
    >>> roundtrip == rsonstr1[1:]    # Get past initial \n
    True

    >>> rsondata2 = rsonlite.loads(rsonstr2)
    >>> roundtrip = rsonlite.dumps(rsondata2, initial_indent='    ')
    >>> roundtrip == rsonstr2[1:]    # Get past initial \n
    True

rsonlite.pretty(data, indent='    ')
---------------------------------------

This pretty-prints a data structure created by loads() for debugging.
The structure is accurate, yet quasi-readable::

    >>> data = rsonlite.loads(rsonstr2)
    >>> pretty = rsonlite.pretty(data)
    >>> print pretty,
    [
        ('menu', [
            ('id', ['file']),
            ('value', ['File']),
            ('popup', [
                ('menuitem', [
                    ('value', ['New']),
                    ('onclick', ['CreateNewDoc()']),
                    ('value', ['Open']),
                    ('onclick', ['OpenDoc()']),
                    ('value', ['Close']),
                    ('onclick', ['CloseDoc()']),
                ])
            ])
        ])
    ]
    >>> eval(pretty) == data
    True
    >>>

rsonlite.simpleparse(source, stringparse=stringparse, stddict=stddict)
------------------------------------------------------------------------

This is a convenience wrapper on loads for simple data structures, and
also provides an example client for loads.  This is the interface that
was used in the JSON example section above.  Parameters:

  source
    source may either be a string that is passed to loads, or a list,
    that is assumed to be the result of running loads on a string.

  stringparse
    stringparse is a function that accepts a (non-key) string, and
    returns a parsed value of the string.  The default example stringparse
    in rsonlite will handle the JSON keywords true, false and null, and
    will also translate really simple arrays of strings, as shown
    in the [GML, XML] example above.

  stddict
    stddict defaults to collections.OrderedDict if available, or a regular
    dict if not.  You may substitute a third-party OrderedDict if desired.

Tests
=======

Empty input::

    >>> rsonlite.loads('') == rsonlite.loads('   \n \n     \n') == []
    True

Bad indentation::

    >>> rsonlite.loads('a\n    b\n  c')
    Traceback (most recent call last):
      File "<doctest README.txt[22]>", line 1, in <module>
        rsonlite.loads('a\n    b\n  c')
      File "/home/pat/projects/opensource/rson/lite/rsonlite.py", line 179, in loads
        raise err
    IndentationError: unindent does not match any outer indentation level (<rsonlite>, line 3)

Multiline data, with special characters::

    >>> teststr = '''
    ...     My key =
    ...            This is indented #=
    ...       This should be at the left edge ===#
    ...           This is indented differently
    ... '''
    >>> test2 = '\n'.join(x[6:] for x in teststr.splitlines()[2:])
    >>> rsonlite.loads(teststr) == [('My key', [test2])]
    True

    >>> teststr = '''
    ...     My key =  Something on the first line is at the left edge
    ...            This is indented
    ...       This should be at the left edge
    ...           This is indented differently
    ... '''
    >>> test2 = teststr.split('=', 1)[1].strip().splitlines()
    >>> for i in range(1, len(test2)):
    ...   test2[i] = test2[i][6:]
    >>> test2 = '\n'.join(test2)
    >>> rsonlite.loads(teststr) == [('My key', [test2])]
    True

Comments and special string stuff::

    >>> test1 = '''
    ...   a
    ...      b = 1
    ...       This is part of b's string
    ...      c
    ...   d = 2
    ... '''
    >>> test2 = '''
    ... # Comments can start anywhere outside a string
    ...   a   # Like here  (but not below)
    ...      b = 1
    ...       This is part of b's string
    ...      # This isn't in the string because it's far enough left
    ...      # Any non-key string can start with '='
    ...      = c
    ...      # This isn't in the string because it's far enough left
    ...   d = 2
    ... '''
    >>> rsonlite.loads(test1) == rsonlite.loads(test2)
    True
