'''
Double-quoted token parser for RSON.

Copyright (c) 2010, Patrick Maupin.  All rights reserved.

See http://code.google.com/p/rson/source/browse/trunk/license.txt
'''


import sys
import re
import bisect
import rson.py23

class QuotedToken(object):
    ''' Subclass or replace this if you don't like quoted string handling
    '''

    parse_quoted_str = staticmethod(rson.py23.to_unicode)
    parse_encoded_chr = rson.py23.unichr
    unicode = rson.py23.unicode
    parse_join_str = unicode('').join
    cachestrings = False

    quoted_splitter = re.compile(r'(\\u[0-9a-fA-F]{4}|\\.|")').split
    quoted_mapper = { '\\\\' : unicode('\\'),
               r'\"' : unicode('"'),
               r'\/' : unicode('/'),
               r'\b' : unicode('\b'),
               r'\f' : unicode('\f'),
               r'\n' : unicode('\n'),
               r'\r' : unicode('\r'),
               r'\t' : unicode('\t')}.get

    def quoted_parse_factory(self, int=int, iter=iter, len=len, next=rson.py23.next):
        quoted_splitter = self.quoted_splitter
        quoted_mapper = self.quoted_mapper
        parse_quoted_str = self.parse_quoted_str
        parse_encoded_chr = self.parse_encoded_chr
        parse_join_str = self.parse_join_str
        cachestrings = self.cachestrings
        triplequoted = self.triplequoted

        allow_double = sys.maxunicode > 65535

        def badstring(token, special):
            if token[2] != '"""' or triplequoted is None:
                token[-1].error('Invalid character in quoted string: %s' % repr(special), token)
            result = parse_quoted_str(token, triplequoted(token))
            if cachestrings:
                result = token[-1].stringcache(result, result)
            return result

        def parse(token, _):
            s = token[2]
            if len(s) < 2 or not (s[0] == s[-1] == '"'):
                token[-1].error('No end quote on string', token)
            s = quoted_splitter(s[1:-1])
            result = parse_quoted_str(token, s[0])
            if len(s) > 1:
                result = [result]
                append = result.append
                s = iter(s)
                next(s)
                for special in s:
                    nonmatch = next(s)
                    remap = quoted_mapper(special)
                    if remap is None:
                        if len(special) == 6:
                            uni = int(special[2:], 16)
                            if 0xd800 <= uni <= 0xdbff and allow_double:
                                uni, nonmatch = parse_double_unicode(uni, nonmatch, s, token)
                            remap = parse_encoded_chr(uni)
                        else:
                            return badstring(token, special)
                    append(remap)
                    append(parse_quoted_str(token, nonmatch))

                result = parse_join_str(result)
            if cachestrings:
                result = token[-1].stringcache(result, result)
            return result


        def parse_double_unicode(uni, nonmatch, s, token):
            ''' Munged version of UCS-4 code pair stuff from
                simplejson.
            '''
            ok = True
            try:
                uni2 = next(s)
                nonmatch2 = next(s)
            except:
                ok = False
            ok = ok and not nonmatch and uni2.startswith(r'\u') and len(uni2) == 6
            if ok:
                nonmatch = uni2
                uni = 0x10000 + (((uni - 0xd800) << 10) | (int(uni2[2:], 16) - 0xdc00))
                return uni, nonmatch2
            token[-1].error('Invalid second ch in double sequence: %s' % repr(nonmatch), token)

        return parse

    @staticmethod
    def triplequoted(token):
        tokens = token[-1]
        source = tokens.source
        result = []
        start = 3 - token[0]
        while 1:
            end = source.find('"""', start)
            if end < 0:
                tokens.error('Did not find end for triple-quoted string', token)
            if source[end-1] != '\\':
                break
            result.append(source[start:end-1])
            result.append('"""')
            start = end + 3
        result.append(source[start:end])
        offset = bisect.bisect(tokens, (- end -2, ))
        tokens[offset:] = []
        return ''.join(result)
