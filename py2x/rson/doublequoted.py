'''
Double-quoted token parser for RSON.

Copyright (c) 2010, Patrick Maupin.  All rights reserved.

See http://code.google.com/p/rson/source/browse/#svn/trunk/license.txt
'''


import re

class QuotedToken(object):
    ''' Subclass or replace this if you don't like quoted string handling
    '''

    makestr = staticmethod(
          lambda token, s, unicode=unicode: unicode(s, 'utf-8'))
    makechr = unichr
    join = u''.join
    cachestrings = False

    splitter = re.compile(r'(\\.)').split
    mapper = { '\\\\' : '\\',
               r'\"' : '"',
               r'\/' : '/',
               r'\b' : '\b',
               r'\f' : '\f',
               r'\n' : '\n',
               r'\r' : '\r',
               r'\t' : '\t',
               r'\u' : None}.get

    @classmethod
    def factory(cls, int=int):
        splitter = cls.splitter
        mapper = cls.mapper
        makestr = cls.makestr
        makechr = cls.makechr
        join = cls.join
        cachestrings = cls.cachestrings

        def parse(token):
            s = token[2]
            if len(s) < 2 or not (s[0] == s[-1] == '"'):
                token[-1].error('No end quote on string', token)
            s = s[1:-1]
            if '\\' not in s:
                result = makestr(token, s)
            else:

                s = [mapper(x, x) for x in splitter(s) if x]
                if None in s:
                    s.append('')
                    s.reverse()
                    next = s.pop
                    result = []
                    append = result.append
                    while s:
                        x = next()
                        if x is not None:
                            append(makestr(token, x))
                            continue
                        x = next()
                        leftovers = x[4:]
                        digits = (x[:4] + 'ZZZZ')[:4]
                        try:
                            value = int(digits, 16)
                        except:
                            token[-1].error('Invalid escaped unicode char: \\u %s' % repr(x[:4]), token)
                        append(makechr(value))
                        append(makestr(token, leftovers))
                else:
                    result = [makestr(token, x) for x in s]
                result = join(result)
            if cachestrings:
                result = token[-1].stringcache(result, result)
            return result

        return parse
