'''
Double-quoted token parser for RSON.

Copyright (c) 2010, Patrick Maupin.  All rights reserved.

See http://code.google.com/p/rson/source/browse/#svn/trunk/license.txt
'''


import sys
import re

class QuotedToken(object):
    ''' Subclass or replace this if you don't like quoted string handling
    '''

    makestr = staticmethod(
          lambda token, s, unicode=unicode: unicode(s, 'utf-8'))
    makechr = unichr
    join = u''.join
    cachestrings = False
    triplequoted = None

    splitter = re.compile(r'(\\u[0-9a-fA-F]{4}|\\.|")').split
    mapper = { '\\\\' : u'\\',
               r'\"' : u'"',
               r'\/' : u'/',
               r'\b' : u'\b',
               r'\f' : u'\f',
               r'\n' : u'\n',
               r'\r' : u'\r',
               r'\t' : u'\t'}.get

    @classmethod
    def factory(cls, int=int, iter=iter, len=len):
        splitter = cls.splitter
        mapper = cls.mapper
        makestr = cls.makestr
        makechr = cls.makechr
        join = cls.join
        cachestrings = cls.cachestrings
        triplequoted = cls.triplequoted

        allow_double = sys.maxunicode > 65535

        def badstring(token, special):
            if token[2] != '"""' or triplequoted is None:
                token[-1].error('Invalid character in quoted string: %s' % repr(special), token)
            return triplequoted(token)

        def parse(token, next):
            s = token[2]
            if len(s) < 2 or not (s[0] == s[-1] == '"'):
                token[-1].error('No end quote on string', token)
            s = splitter(s[1:-1])
            result = makestr(token, s[0])
            if len(s) > 1:
                result = [result]
                append = result.append
                s = iter(s)
                next = s.next
                next()
                for special in s:
                    nonmatch = next()
                    remap = mapper(special)
                    if remap is None:
                        if len(special) == 6:
                            uni = int(special[2:], 16)
                            if 0xd800 <= uni <= 0xdbff and allow_double:
                                uni, nonmatch = parse_double(uni, nonmatch, next, token)
                            remap = makechr(uni)
                        else:
                            return badstring(token, special)
                    append(remap)
                    append(makestr(token, nonmatch))

                result = join(result)
            if cachestrings:
                result = token[-1].stringcache(result, result)
            return result


        def parse_double(uni, nonmatch, next, token):
            ''' Munged version of UCS-4 code pair stuff from
                simplejson.
            '''
            ok = True
            try:
                uni2 = next()
                nonmatch2 = next()
            except:
                ok = False
            ok = ok and not nonmatch and uni2.startswith(r'\u') and len(uni2) == 6
            if ok:
                nonmatch = uni2
                uni = 0x10000 + (((uni - 0xd800) << 10) | (int(uni2[2:], 16) - 0xdc00))
                return uni, nonmatch2
            token[-1].error('Invalid second ch in double sequence: %s' % repr(nonmatch), token)

        return parse
