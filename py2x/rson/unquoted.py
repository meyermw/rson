'''
Unquoted token parser for RSON.

Copyright (c) 2010, Patrick Maupin.  All rights reserved.
'''

import re

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

    parse_int = staticmethod(
        lambda s: int(s.replace('_', ''), 0))
    parse_float = float
    parse_unquoted_str = staticmethod(
        lambda token, unicode=unicode: unicode(token[2], 'utf-8'))

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

    @classmethod
    def factory(cls):
        unquoted_match = re.compile(cls.unquoted_pattern,
                        re.VERBOSE).match

        parse_unquoted_str = cls.parse_unquoted_str
        parse_float = cls.parse_float
        parse_int = cls.parse_int
        special = cls.special_strings

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



class StrictUnquotedToken(UnquotedToken):
    ''' Strict JSON-only token syntax, using
        diagram at json.org
    '''

    parse_int = lambda s: int(s, 0)

    @staticmethod
    def parse_unquoted_str(token):
        token[-1].error('Invalid literal', token)


    unquoted_pattern = r'''
    (?:
        true | false | null       |     # Special JSON names
        (?P<num>
            -?                          # Optional minus sign
            (?:0|[1-9]\d*)              # Zero or digits with non-zero lead
            (?P<float>
               (?:\.\d+)?               # Optional frac part
               (?:[eE][-+]?\d+)?        # Optional exponent
            )
        )
    )  \Z                               # Match end of string
    '''

class CompatibleUnquotedToken(StrictUnquotedToken):
    ''' Compatible JSON-only token syntax,
        tries to work same as simplejson
    '''

    unquoted_pattern = StrictUnquotedToken.unquoted_pattern.replace('true',
            'true | Infinity')
    special_strings = StrictUnquotedToken.special_strings.copy()
    for x in 'Infinity NaN'.split():
        special_strings[x] = float(x)
