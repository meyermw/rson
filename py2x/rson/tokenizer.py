'''
Tokenizer for RSON.

Copyright (c) 2010, Patrick Maupin.  All rights reserved.
'''

# XXX: TODO:  RECURSE ON NON-COMMENT-STARTING #

import re

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
    indentation = r'\n[ \t\v\f\v]*'

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

    # Comments (where allowed) consist of the # and all the remaining
    # characters on the same line.
    comment = r'(?:^|\s)#.*'

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
      comment,
      other
    ])

    splitter = re.compile(pattern).split

    @classmethod
    def factory(cls, len=len, iter=iter):
        splitter = cls.splitter
        delimiterset = set(cls.delimiterset) | set('"')

        def newstring(source, client):
            self = cls()

            # Convert MS-DOS or Mac line endings to the one true way
            source = source.replace('\r\n', '\n').replace('\r', '\n')

            # Set up to iterate over the source and add to the destination list
            sourceiter = iter(splitter(source))
            next = sourceiter.next
            append = self.append

            # Get the indentation at the start of the file
            indentation = '\n' + next()
            offset = 1 - len(indentation)
            linestart = offset
            linenum = 1

            # Create all the rest of the tokens
            for token in sourceiter:
                whitespace = next()
                t0 = token[0]
                if t0 in delimiterset:
                    append((offset, t0, token, whitespace, indentation, linenum, client))
                elif t0 not in '\n#':
                    append((offset, 'X', token, whitespace, indentation, linenum, client))
                elif t0 == '\n':
                    linenum += 1
                    indentation = token
                    offset -= len(token)
                    linestart = offset
                    continue
                else:
                    # Must be comment (#)
                    # Either strip it or consider it just more potential unquoted string stuff
                    if linestart != offset:
                        append((offset, '#', token, whitespace, indentation, linenum, client))
                offset -= len(token) + len(whitespace)

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
