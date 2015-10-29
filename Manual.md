# Readable Serial Object Notation  (RSON) #

Version 0.9

Copyright (c) 2010-2012 Patrick Maupin

# Introduction #

RSON is a superset of the JSON data format.

RSON syntax is relaxed compared to JSON:

  * Any valid JSON file is also a valid RSON file as long as it is encoded in UTF-8 or ASCII.  (External conversion functions could detect other files and pass UTF-8 or Unicode to the RSON decoder.)
  * Comments are allowed with a leading **#** (in any column) if the comment is the only non-whitespace on the line. (But inside a triple-quoted or equal-delimited string, the # may not always start a comment -- it may be part of the string.)
  * String quoting is not required unless the string contains any RSON special characters. RSON special characters are: ` { } [ ] : , " = `  (The same as the JSON special characters, plus `=`.)
  * Python-style triple-quoted (**"""**) strings are supported for practically arbitrary embedded data.
  * Integer formats include hex, binary, and octal, and embedded underscores are allowed.


In addition to the relaxed JSON syntax, RSON supports Python-style indentation to create structures.  When _inside_ any **[.md](.md)** or **{}** pair, the syntax is JSON syntax, with the enhancements described above.  _Outside_ any **[.md](.md)** or **{}** pairs, RSON indented syntax is used to describe the structure.

RSON indentation controls the nesting levels of dicts or lists.  As with Python, spaces or tabs may be used (in fact, any valid JSON whitespace except \n or \r may be used for any whitespace, including indentation),  but RSON does not make any equivalence between tabs and spaces, so indenting a line the same as or more than a previous line requires prefixing the line with exactly the same whitespace characters as were used on the previous line.  Mixing tab and space (or other) indentation whitespace will most likely result in an error.

# Examples #

The examples all show RSON syntax, followed by the equivalent JSON, which is calculated by using the RSON decoder and the simplejson encoder on the RSON string.

The simple array:

```
1
2
3
```

Results in the following equivalent JSON:

```
[
  1,
  2,
  3
]
```

The two-dimensional array:

```
[1, 2, 3]
[4, 5, 6]
[7, 8, 9]
[a, b, c]
```

Results in the following equivalent JSON:

```
[
  [
    1,
    2,
    3
  ],
  [
    4,
    5,
    6
  ],
  [
    7,
    8,
    9
  ],
  [
    "a",
    "b",
    "c"
  ]
]
```

Nested dictionaries:

```
George:
    age:     42
    height:  6'2"
    weight:  232
Sam:
    age:     13
    height:  5'1"
    weight:  103.5
Morrie:
    age:     0.7
    height:  0.5"
    weight:  1.5oz
```

Results in the following equivalent JSON:

```
{
  "Morrie": {
    "age": 0.69999999999999996,
    "weight": "1.5oz",
    "height": "0.5\""
  },
  "George": {
    "age": 42,
    "weight": 232,
    "height": "6'2\""
  },
  "Sam": {
    "age": 13,
    "weight": 103.5,
    "height": "5'1\""
  }
}
```

Windows-registry-style keys:

```
evilness:high:starter
    cmd1 = cd /
    cmd2 = rm -Rf *

evilness:high:more subtle
    cmd1 = cd /etc
    cmd2 = rm *pass*

evilness:low:silly:
    cmd1 = cat < /dev/random > /dev/null

windows:registry:some:randomly:nested:deep:program
    # If it's Windows, use lots of spaces and special chars
    # in your excessively long filename
    backwards file name = c:\your\favorite\path\here(&there??).exe
```

Results in the following equivalent JSON:

```
{
  "windows": {
    "registry": {
      "some": {
        "randomly": {
          "nested": {
            "deep": {
              "program": {
                "backwards file name": "c:\\your\\favorite\\path\\here(&there??).exe"
              }
            }
          }
        }
      }
    }
  },
  "evilness": {
    "high": {
      "more subtle": {
        "cmd1": "cd /etc",
        "cmd2": "rm *pass*"
      },
      "starter": {
        "cmd1": "cd /",
        "cmd2": "rm -Rf *"
      }
    },
    "low": {
      "silly": {
        "cmd1": "cat < /dev/random > /dev/null"
      }
    }
  }
}
```

Arbitrary strings:

```
George:
    age:     42
    height:  6'2"
    weight:  232
    comment: """
  Python style triple quotes leave data intact"""

Sam:
    age:     13
    height:  5'1"
    weight:  103.5

Morrie:
    age:     0.7
    height:  0.5"
    weight:  1.5oz
    comment = Equals strings have some trimming.

      Morrie is a goldfish.
```

Results in the following equivalent JSON:

```
{
  "Morrie": {
    "comment": "Equals strings have some trimming.\n\nMorrie is a goldfish.\n",
    "age": 0.69999999999999996,
    "weight": "1.5oz",
    "height": "0.5\""
  },
  "George": {
    "comment": "\n      Python style triple quotes leave data intact",
    "age": 42,
    "weight": 232,
    "height": "6'2\""
  },
  "Sam": {
    "age": 13,
    "weight": 103.5,
    "height": "5'1\""
  }
}
```

Array of arbitrary strings:

```
# The triple quoted string does absolutely nothing to
# intervening data
""" Here is a
        string with trailing spaces   """

# The equal string does special processing.
# If the '#' is far enough to the right, it
# is part of the string:
= John Doe
  123 Main Street
# The following is an apartment number
  #120
  Anytown, USA 12345

# Another thing that = does special is to treat
# any multi-line = as a string, while allowing
# a single line = to be another kind of scalar.
# See the section on syntax for scalars further down.

= 5.0
=
  5.0

A string that fits on one line and has no special characters
does not need to be quoted at all.
"A regular JSON string can use all the JSON escapes"
```

Results in the following equivalent JSON:

```
[
  " Here is a\n            string with trailing spaces   ",
  "John Doe\n123 Main Street\n#120\nAnytown, USA 12345\n",
  5.0,
  "5.0\n",
  "A string that fits on one line and has no special characters",
  "does not need to be quoted at all.",
  "A regular JSON string can use all the JSON escapes"
]
```

Nested arrays and dicts:

```
1
2
[]
   a
   b
   c
{}
   z: x
   w: []
       m
```

Results in the following equivalent JSON:

```
[
  1,
  2,
  [
    "a",
    "b",
    "c"
  ],
  {
    "z": "x",
    "w": [
      "m"
    ]
  }
]
```

# Syntax rules #

## Extended JSON ##

Inside any **[.md](.md)** or **{}** pairs, the syntax is extended JSON, as described in the [Introduction](#introduction.md) and further discussed in [Scalars (numbers, strings, true, false, null)](#scalars-numbers-strings-true-false-null.md).

## Indented RSON ##

Outside any **[.md](.md)** or **{}** delimiter pairs, the following rules apply:

  * A group of lines at the same indentation level (which continues past any lines which are indented more, but stops on the first line which is indented less), either comprises:
    * A dict (JSON object)
> The group of lines at a given indentation level is considered to be a dict if the first line _contains_ a key/value pair (a key, followed by **:** or **=** and a value), or _starts_ a key/value pair (contains a key, and is followed by one or more indented lines comprising the value).

  * A single scalar (JSON string or number, or true, false, or null)
> If the group of lines cannot be interpreted as a dict, and consists of a single line, or a single triple-quoted or equal-prefixed string.

  * A list (JSON array)
> If the group of lines cannot be interpreted as a dict or single scalar, and contains more than one line.

  * An equal sign may be used to denote the start of a value scalar.  The string representing this scalar extends to the end of the line, and through any more-indented lines until a line at the same or lesser indentation as the line containing the equal sign is found.  This value scalar cannot be the key of a key/value pair, because the syntax is such that any trailing colon or indented lines are actually part of the scalar value, and not syntactically meaningful to RSON.
> This equal-sign prefixed scalar string is trimmed both horizontally and vertically.  (See the section on scalars.)
    * A colon is used to separate a key from its value.  This can be done repeatedly, e.g:
```
a:b:c:d
a:b:e:f
```

> Results in the following equivalent JSON:
```
{
  "a": {
    "b": {
      "c": "d",
      "e": "f"
    }
  }
}
```

  * A colon will be assumed if one is not present between a key and an equal sign which denotes the start of a value scalar.
  * A colon will also be assumed if not present between a key and group of lines that is more indented than the line the key is on.  (But see [Empty Lists and Dicts](#empty-lists-and-dicts.md), below, for exceptions.)


## Empty Lists and Dicts ##

Sometimes, an array is required that has some array elements and some non-array elements, e.g. _[1, 2, 3, [a, b, c]]_.

To support this, whenever a text file line is more deeply indented than the previous line, RSON examines the last value on the previous line. If that previous value is an _empty_ dict or array, then the indented lines are added into that structure.  In all other cases, the previous line is considered to be a key (or set of keys for a nested dict structure), and the indented lines comprise the value for a dictionary.

For example:

```
1
2
3
[]
    a
    b
    c
{}
    d:e
    f:g
4
5
```

Results in the following equivalent JSON:

```
[
  1,
  2,
  3,
  [
    "a",
    "b",
    "c"
  ],
  {
    "d": "e",
    "f": "g"
  },
  4,
  5
]
```

## Scalars (numbers, strings, true, false, null) ##

RSON scalar support is highly modularized and easily replaceable by the application.  But the higher-level scalar syntax is fixed:

  * Data inside double-quotes forms a scalar.
  * Data which does not contain any RSON delimiters ( **{** **}** **[** **]** **:** **=** **,** ) and which does not start with a quote (**"**) forms a scalar.  This unquoted scalar starts at a non-blank character and ends at the last non-blank character before the next RSON delimiter or the end of the line, whichever comes first.
  * Data following an equal sign (**=**), and subsequent indented lines, forms a scalar in indented syntax mode (but not in extended JSON mode inside **{}** or **[.md](.md)**).


The default RSON handling for scalars separates them into 4 types for processing.  (Quoted strings have two subtypes.):

  * Normal JSON strings, e.g. "this is a string" support all the JSON string escape sequences.
  * Python style triple-quoted strings, e.g. """this is also a string""" support almost arbitrary data inclusion.  The only special handling between the starting """ and the ending """ is that any occurrence of **\"""** is replaced with **"""**.
  * Unquoted scalars are tested to see if they are a supported numeric format (see next section) or if they are the JSON-defined constants 'true', 'false', or 'null'.  If not, they are returned as strings.
  * Scalars prefixed with '=' are trimmed, both horizontally and vertically. The default rules are a little complicated, but basically will normally give you what you expect.  Any application can create a function for handling the = scalar data if this is not the case.  After special '=' processing, by default the data is passed to the same function which handles regular unquoted scalars. So, by default, if all the data is on the same line as the '=', it is checked to see if it is a special object or a number.


In addition to strings, RSON supports the following scalar values for unquoted strings, and strings following '=' on a single line:

  * 'true', 'false', 'null'  These JSON standard strings are converted to Python True, False, and None.
Integers and floats.  The JSON syntax for these is supported.  In addition:
    * Integers may be in decimal, hexadecimal, octal, or binary, with 0x, 0o, or 0b prefixes.
    * Leading zeros are allowed where they would not be in JSON
    * Integers may have embedded underscores
    * Floats may start with the decimal point (leading zero not required).
    * The Python json library extension of supporting Infinity and Nan is not supported by default.



# Implementation and use #

There is a Python RSON decoder available, which can be downloaded from [googlecode](http://code.google.com/p/rson/). You can also use 'pip rson' or 'easy\_install rson' to download it.  It works with both Python 2 and Python 3 from a single codebase.

The base profile of the decoder works like the JSON decoder:

from rson import loads

result = loads(source)

The decoder is built in a manner that facilitates replacing parts of the decoder, as necessary.  For example, you could easily use the Decimal class instead of floats.  It supports many of the same options as json/simplejson.  In fact, a subclassed version of the decoder passes the simplejson regression suite.

Currently, there is no generic RSON encoder, although there is an example one available in the [rst2pdf package](http://code.google.com/p/rst2pdf/source/browse/trunk/rst2pdf/dumpstyle.py) that will dump the stylesheets and/or convert old-style JSON stylesheets into RSON.  The purpose of RSON is to look nice, and what "looks nice" is application-specific.

# Future plans #

RSON is a work in progress.  A more general purpose encoder may be built at some point, but most changes will be driven by user feedback to the rson-discuss google group.

RSON has proven invaluable for building mini-declarative languages, and some of these will be made available as additional profiles in addition to the base profile.
