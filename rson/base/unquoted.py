'''
Unquoted token parser for RSON.

Copyright (c) 2010, Patrick Maupin.  All rights reserved.

See http://code.google.com/p/rson/source/browse/trunk/license.txt
'''

import re
import rson.py23

class UnquotedToken(object):
    ''' Subclass or replace this if you don't like the unquoted
        token handling.  This is designed to be a superset of JSON:

          - Integers allowed to be expressed in octal, binary, or hex
            as well as decimal.

          - Integers can have embedded underscores.

          - Non-match of a special token will just be wrapped as a unicode
            string.

          - Numbers can be preceded by '+' as well s '-'
          - Numbers can be left-zero-filled
          - If a decimal point is present, digits are required on either side,
            but not both sides
    '''

    use_decimal = False
    parse_int = staticmethod(
        lambda s: int(s.replace('_', ''), 0))
    parse_float = float
    parse_unquoted_str = staticmethod(rson.py23.to_unicode2)

    special_strings = dict(true = True, false = False, null = None)

    unquoted_pattern = r'''
    (?:
        true | false | null       |     # Special JSON names
        (?P<num>
            [-+]?                       # Optional sign
            (?:
                0[xX](_*[0-9a-fA-F]+)+   | # Hex integer
                0[bB](_*[01]+)+          | # binary integer
                0[oO](_*[0-7]+)+         | # Octal integer
                \d+(_*\d+)*              | # Decimal integer
                (?P<float>
                    (?:
                      \d+(\.\d*)? |     # One or more digits,
                                        # optional frac
                      \.\d+             # Leading decimal point
                    )
                    (?:[eE][-+]?\d+)?   # Optional exponent
                )
            )
        )
    )  \Z                               # Match end of string
    '''

    def unquoted_parse_factory(self):
        unquoted_match = re.compile(self.unquoted_pattern,
                        re.VERBOSE).match

        parse_unquoted_str = self.parse_unquoted_str
        parse_float = self.parse_float
        parse_int = self.parse_int
        special = self.special_strings

        if self.use_decimal:
            from decimal import Decimal
            parse_float = Decimal

        def parse(token, next):
            s = token[2]
            m = unquoted_match(s)
            if m is None:
                return parse_unquoted_str(token)
            if m.group('num') is None:
                return special[s]
            if m.group('float') is None:
                return parse_int(s.replace('_', ''))
            return parse_float(s)

        return parse
