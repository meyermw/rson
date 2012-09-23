#!/usr/bin/env python
'''
Test code for to run rson against simplejson testsuite.

Copyright (c) 2010, Patrick Maupin.  All rights reserved.

See http://code.google.com/p/rson/source/browse/trunk/license.txt

'''


import sys
import re

sys.path[0:0] = '..', '../../../simplejson'

import simplejson
import simplejson.tests
import rson

# For some reason, the only test that simplejson does
# on actual file location uses a different location than
# we do, so we fudge our location.  (They test on '[,]',
# and claim an error on the '[', but RSON errors on the ','.)

oldloc = rson.Tokenizer.sourceloc
def sourceloc(token):
    offset, lineno, colno = oldloc(token)
    return offset-1, lineno, max(colno-1, 1)
rson.Tokenizer.sourceloc = staticmethod(sourceloc)

class CJsonSystem(rson.RsonSystem):
    ''' Compatible JSON-only token syntax,
        tries to work same as simplejson
    '''

    # These are simple things that simplejson does

    cachestrings = True
    parse_int = int
    disallow_multiple_object_keys = True

    # simplejson requires an unquoted literal to be
    # a number or one of the special values like true
    # or false, so report an error instead of wrapping
    # something not in those categories into a string.

    @staticmethod
    def parse_unquoted_str(token):
        token[-1].error('Invalid literal', token)


    # Follow the JSON syntax for unquoted literals,
    # plus add the simplejson Infinity and NaN.
    # (Stock RSON does not use Infinity or NaN, and
    # allows relaxed numeric patterns, including:
    #   - extra leading zeros on numbers
    #   - Missing 0 in front decimal point for floats
    #   - hex, binary, octal ints
    #   - embedded underscores in ints.)
    # These features do not work with simplejson.

    unquoted_pattern = r'''
    (?:
        true | false | null       |     # Special JSON names
        Infinity | NaN            |
        (?P<num>
            -?                          # Optional minus sign
            (?:0|[1-9]\d*)        |     # Zero or digits with non-zero lead
            (?P<float>
               -?                       # Optional minus sign
               (?:0|[1-9]\d*)
               (?:\.\d+)?               # Optional frac part
               (?:[eE][-+]?\d+)?        # Optional exponent
            )
        )
    )  \Z                               # Match end of string
    '''

    # The special_strings dict has Infinity and Nan added to it.

    special_strings = dict(true = True, false = False, null = None,
                           Infinity = float('inf'), NaN = float('NaN'))

    # RSON does not care about weird control characters embedded in strings.
    # To pass the simplejson test suite, make it care about \x1f.

    quoted_splitter = re.compile(r'(\\u[0-9a-fA-F]{4}|\\.|"|[\x1f])').split

simplejson.loads = CJsonSystem.dispatcher_factory()
simplejson.JSONDecodeError = rson.RSONDecodeError
simplejson.tests.main()
