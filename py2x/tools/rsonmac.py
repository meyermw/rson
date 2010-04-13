#!/usr/bin/env python
'''
An example script for RSON that handles macros and include files.

This could use a bit better error reporting, etc. but is basically functional.

TODO:
    - Use RSON error reporting
    - Perhaps move under RSON, and start distributing RSON as a package rather
      than a single module.
    - Figure out way to specify an include path
    - Maybe make it where you don't need to do str()

Copyright (c) 2010, Patrick Maupin.  All rights reserved.

See http://code.google.com/p/rson/source/browse/trunk/license.txt

Usage:

When the loads() inside this file is used, any string which is unquoted and which
doesn't follow "=" is checked for the following special cases:

  - If it starts with @, it references another rson file which is included
  - If it contains $, then macro processing is performed.

Macro processing uses the following special characters:

  - $xxxx   starts a macro, which ends on the first character which is not in A-Za-z0-9_[].
  - $(xxx)  contains a macro

Within a macro, the characters .[] are special.  They are all separator characters between
macro identifiers.

Macros can reference any data in the same file that:

  - has already been encountered; and
  - is not in the same nested RSON structure

If the the data is in the same nested RSON structure, it can be used, but
must be dereferenced later (e.g. via str()).  This doesn't work for macros
used in include file names, where the names must be in a different top-level
RSON structure than anything using the name via $
'''


import sys
import re
sys.path.insert(0, '..')
from rson import RsonSystem

class StringProxy(object):
    macro_special_chars = '[]().$'
    macro_split = re.compile(r'([A-Za-z0-9_]+|%s)' % '|'.join('\\'+x for x in macro_special_chars)).split

    def __init__(self, token):
        self.token = token

    @property
    def dereference(self):
        token = self.token
        top_obj = token[-1].top_object
        strings = [x for x in self.macro_split(token[2]) if x]
        strings = iter(strings)
        result = []

        def recurse(result, endch=None):
            for s in strings:
                while s == '$':
                    s = handle_dollar(result)
                if s == endch:
                    return s
                result.append(s)


        def handle_dollar(result):
            lookup = []
            gotparen = False
            for s in strings:
                if s == '$':
                    if not lookup:
                        result.append('$$')
                        return ''
                    break
                elif s.replace('_', '').isalnum():
                    lookup.append(s)
                    s = ''
                elif s == '[':
                    s = recurse(lookup, ']')
                    assert s == ']'
                    s = ''
                elif s == '.':
                    continue
                elif s == '(' and not lookup:
                    gotparen = True
                else:
                    break
            if gotparen:
                assert s == ')'
                s = ''
            nexts = s

            myobj = top_obj
            for s in lookup:
                try:
                    ints = int(s)
                except ValueError:
                    pass
                else:
                    try:
                        myobj = myobj[ints]
                    except:
                        pass
                    else:
                        continue
                myobj = myobj[s]
            result.append(myobj)
            return nexts

        result = []
        recurse(result)
        if len(result) == 1:
            return result[0]
        return ''.join(str(x) for x in result)

    def __repr__(self):
        return unicode(self.dereference, 'utf-8')

class RsonMacros(RsonSystem):
    @classmethod
    def parse_unquoted_str(cls, token, unicode=unicode):
        s = token[2]
        if token[1] != '=':
            if s.startswith('@'):
                return cls.handle_include(token)
            if '$' in s:
                return cls.handle_macro(token)
        return unicode(s, 'utf-8')

    @classmethod
    def handle_include(cls, token):
        token = list(token)
        token[2] = token[2][1:]
        assert token[2] and not token[2].startswith('@'), token[2]
        fname = cls.parse_unquoted_str(tuple(token))
        # Do whatever stuff you want here to fix the filename up
        # (look in the current directory, whatever)
        f = open(fname, 'rb')
        data = f.read()
        f.close()
        return loads(data)

    @staticmethod
    def handle_macro(token):
        value = StringProxy(token)
        try:
            return value.dereference
        except:
            return value

loads = RsonMacros.dispatcher_factory()

if __name__ == '__main__':
    test1 = '''
fnames: []
    foobar.txt
foobar: @$fnames[0]
messages:
    {}
        stream: sys.stderr
        message: Welcome
    {}
        stream : $messages[0].stream
        message: Bienvenue
    '''
    print loads(test1)
