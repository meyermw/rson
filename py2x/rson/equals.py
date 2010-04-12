'''
Equals sign string processor for RSON.

Copyright (c) 2010, Patrick Maupin.  All rights reserved.

See http://code.google.com/p/rson/source/browse/trunk/license.txt

'''

class EqualToken(object):
    ''' Subclass or replace this if you don't like the = string handling
    '''

    encode_equals_str = None

    @staticmethod
    def parse_equals(stringlist, indent, token):
        ''' token probably not needed except maybe for error reporting.
            Replace this with something that does what you want.
        '''
        # Strip any trailing whitespace to the right
        stringlist = [x.rstrip() for x in stringlist]

        # Strip any embedded comments
        stringlist = [x for x in stringlist if x.startswith(indent) or not x]

        # Strip trailing whitespace down below
        while stringlist and not stringlist[-1]:
            stringlist.pop()

        # Special cases for single line
        if not stringlist:
            return ''
        if len(stringlist) == 1:
            return stringlist[0].strip()

        # Strip whitespace on first line
        if stringlist and not stringlist[0]:
            stringlist.pop(0)

        # Dedent all the strings to one past the equals
        dedent = len(indent)
        stringlist = [x[dedent:] for x in stringlist]

        # Figure out if should dedent one more
        if min((not x and 500 or len(x) - len(x.lstrip())) for x in stringlist):
            stringlist = [x[1:] for x in stringlist]

        # Give every line its own linefeed (keeps later parsing from
        # treating this as a number, for example)
        stringlist.append('')

        # Return all joined up as a single unicode string
        return '\n'.join(stringlist)

    def equal_parse_factory(self, read_unquoted):

        parse_equals = self.parse_equals
        encoder = self.encode_equals_str

        if encoder is None:
            encoder = read_unquoted

        def parse(firsttok, next):
            tokens = firsttok[-1]
            indent, linenum = firsttok[4:6]
            token = next()
            while token[5] == linenum:
                token = next()
            while  token[4] > indent:
                token = next()
            tokens.push(token)

            # Get rid of \n, and indent one past =
            indent = indent[1:] + ' '

            bigstring = tokens.source[-firsttok[0] + 1 : -token[0]]
            stringlist = bigstring.split('\n')
            stringlist[0] = indent + stringlist[0]
            token = list(firsttok)
            token[1:3] = '=', parse_equals(stringlist, indent, firsttok)
            return encoder(token, next)

        return parse
