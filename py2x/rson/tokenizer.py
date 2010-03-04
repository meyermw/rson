'''
Tokenizer for RSON.

Copyright (c) 2010, Patrick Maupin.  All rights reserved.
'''

import re

class RSONDecodeError(ValueError):
    pass

class Tokenizer(list):
    ''' The RSON tokenizer uses re.split() to rip the source string
        apart into smaller strings which may or may not be true standalone
        tokens.  Sufficient information is maintained to put Humpty-Dumpty
        back together when necessary.

        The tokens are kept in a reversed list.  This makes retrieving
        the next token a low-cost pop() operation from the end of the list,
        and facilitates arbitrary lookahead operations.

        Each token is a tuple, containing the following elements:
           [0] Negative character offset of token within the source string.
               A negative offset is used so that the tokens are sorted
               properly for bisect() for special operations.
           [1] single-character string usually containing a character
               which represents the token type (often the entire token).
           [2] string containing entire token
           [3] string (possibly null) containing whitespace after token
           [4] Indentation value of line containing token
                            (\n followed by 0 or more spaces)
           [5] Line number of token
           [6] Object that the token belongs to (for error reporting)
    '''

    # Like Python, indentation is special.  I originally planned on making
    # the space character the only valid indenter, but that got messy
    # when combined with the desire to be 100% JSON compatible, so, like
    # JSON, you can indent with any old whitespace, but if you mix and
    # match, you might be in trouble (like with Python).
    #
    # An indentation is always the preceding EOL plus optional spaces,
    # so we create a dummy EOL for the very start of the string.
    # Could also have an embedded comment
    indentation = r'\n[ \t\v\f\v]*(?:#.*)?'

    # JSON-syntax delimiters are tokenized separately from everything else.
    delimiterset = set(' { } [ ] / : = , '.split())

    # Create a RE pattern for the delimiters
    delimiter_pattern = '|'.join(r'\%s' % x for x in delimiterset)

    # A regular quoted string must terminate before the end of the line,
    # and \ can be used as the internal escape character.
    quoted_string = r'"(?:[^"\n\\]|\\.)*(?:"|(?=\n))'

    # A triple-quoted string can contain any characters.  The only escape
    # processing that is done on them is to allow a backslash in front of
    # another set of triple quotes.  We only look for the start of one of
    # these suckers in the first pass, and then go find the real string
    # later.  This keeps us from getting our knickers in a twist on
    # regular strings vs triple-quoted vs comments, etc.

    triple_quoted_string = '"""'

    # Any non-whitespace, non-delimiter, group of characters is in the "other"
    # category.  This group can have embedded whitespace, but ends on a
    # non-whitespace character.

    re_delimiterset = ''.join(delimiterset).replace(']', r'\]')

    other = r'[\S](?:[^%s\n]*[^%s\s])*' % (re_delimiterset, re_delimiterset)

    pattern = '(%s)' % '|'.join([
      indentation,
      delimiter_pattern,
      triple_quoted_string,
      quoted_string,
      other
    ])

    splitter = re.compile(pattern).split

    @classmethod
    def factory(cls, len=len, iter=iter, unicode=unicode, isinstance=isinstance):
        splitter = cls.splitter
        delimiterset = set(cls.delimiterset) | set('"')

        def newstring(source, client):
            self = cls()

            # Deal with 8 bit bytes for now
            if isinstance(source, unicode):
                source = source.encode('utf-8')

            # Convert MS-DOS or Mac line endings to the one true way
            source = source.replace('\r\n', '\n').replace('\r', '\n')
            sourcelist = splitter(source)

            # Get the indentation at the start of the file
            indentation = '\n' + sourcelist[0]
            linenum = 1
            linestart = offset = 0

            # Set up to iterate over the source and add to the destination list
            sourceiter = iter(sourcelist)
            next = sourceiter.next
            append = self.append
            offset -= len(next())

            # Strip comment from first line
            if len(sourcelist) > 1 and sourcelist[1].startswith('#'):
                i = 1
                while len(sourcelist) > i and not sourcelist[i].startswith('\n'):
                    i += 1
                    offset -= len(next())
                    
            # Create all the tokens
            for token in sourceiter:
                whitespace = next()
                t0 = token[0]
                if t0 != '\n':
                    if t0 not in delimiterset:
                        t0 = 'X'
                    append((offset, t0, token, whitespace, indentation, linenum, client))
                    offset -= len(token) + len(whitespace)
                else:
                    linenum += 1
                    indentation = token
                    offset -= len(token)
                    linestart = offset

            # Add a sentinel
            append((offset, '@', '@', '', '', linenum, client))

            # Put everything we need in the actual object instantiation
            self.reverse()
            self.source = source
            self.next = self.pop
            self.push = self.append
            return self
        return newstring

    def peek(self):
        return self[-1]

    def lookahead(self, index=0):
        return self[-1 - index]

    @staticmethod
    def error(s, token):
        ''' error performs generic error reporting for tokens
        '''
        lineno = token[5]
        colno = offset = -token[0]
        if lineno != 1:
            colno -= token[-1].tokens.source.rfind('\n', offset)
        if token[1] == '@':
            loc = 'at end of string'
        else:
            text = token[2]
            loc = 'line %s, column %s, text %s' % (lineno, offset, repr(text[:20]))

        err = RSONDecodeError('%s: %s' % (s, loc))
        err.pos = offset
        err.lineno = lineno
        err.colno = colno
        raise err

