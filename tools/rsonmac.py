#!/usr/bin/env python
'''
An example script for RSON that handles macros and include files.

This could use a bit better error reporting, etc. but is basically functional.

TODO:
    - Use RSON error reporting
    - Perhaps move under RSON, and start distributing RSON as a package rather
      than a single module.
    - Figure out way to specify an include path

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
'''


import sys
import re
sys.path.insert(0, '..')
from rson import RsonSystem, Tokenizer
from rson.baseobjects import make_hashable

class MacroProxy(object):
    macro_special_chars = '[]().$'
    macro_split = re.compile(r'([A-Za-z0-9_]+|%s)' % '|'.join('\\'+x for x in macro_special_chars)).split
    actual = None

    def __init__(self, token):
        self.token = token

    def findobj(self, lookup):
        myobj = self.token[-1].top_object
        for s in lookup:
            try:
                index = int(s)
                myobj[index]
            except:
                index = str(s)
            subobj = myobj[index]
            if isinstance(subobj, type(self)):
                myobj[index] = subobj = subobj.dereference()
            myobj = subobj
        return myobj

    def handle_macro(self, s):
        strings = [x for x in self.macro_split(s) if x]
        strings = iter(strings)
        result = []

        def recurse(result, endch=None):
            for s in strings:
                while s == '$':
                    s = handle_dollar(result)
                if s == endch:
                    return s
                result.append(unicode(s, 'utf-8'))

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
            result.append(self.findobj(lookup))
            return s

        result = []
        recurse(result)
        if len(result) == 1:
            result = result[0]
        result = u''.join(unicode(x) for x in result)
        return result

    def handle_include(self, s):
        client_info = self.token[-1].client_info
        assert s and not s.startswith('@'), s
        fname = self.handle_macro(s)
        # Do whatever stuff you want here to fix the filename up
        # (look in the current directory, whatever)
        # Suggested to use client_info to store search path.
        f = open(fname, 'rb')
        data = f.read()
        f.close()
        return client_info.parse(data)

    def dereference(self):
        if self.actual is not None:
            return self.actual
        s = self.token[2]
        if s.startswith('@'):
            result = self.handle_include(s[1:])
        else:
            result = self.handle_macro(s)
        self.actual = result
        return result

class RsonMacros(RsonSystem):

    class Tokenizer(Tokenizer):
        def __init__(self):
            self.proxylist = []

    def client_info(self, parse_locals):
        class Info(object):
            parse = staticmethod(parse_locals['parse'])
        return Info

    @staticmethod
    def post_parse(tokens, value):
        for obj, index in tokens.proxylist:
            subobj = obj[index]
            if isinstance(subobj, MacroProxy):
                obj[index] = subobj.dereference()
        return value

    class default_array(list):
        def __init__(self, startlist, token):
            if token is not None:
                self.proxylist = token[-1].proxylist
            list.__init__(self)
            for value in startlist:
                self.append(value)
        def append(self, value):
            if isinstance(value, MacroProxy):
                self.proxylist.append((self, len(self)))
            list.append(self, value)

    class default_object(dict):
        ''' By default, RSON objects are dictionaries that
            allow attribute access to their existing contents.
        '''
        def __init__(self):
            self.proxylist = []

        def append(self, itemlist):
            mydict = self
            value = itemlist.pop()
            itemlist = [make_hashable(x) for x in itemlist]
            lastkey = itemlist.pop()

            if itemlist:
                itemlist.reverse()
                while itemlist:
                    key = itemlist.pop()
                    subdict = mydict.get(key)
                    if not isinstance(subdict, dict):
                        subdict = mydict[key] = type(self)()
                    mydict = subdict
            if isinstance(value, dict):
                oldvalue = mydict.get(lastkey)
                if isinstance(oldvalue, dict):
                    oldvalue.update(value)
                    return
            mydict[lastkey] = value
            if isinstance(value, MacroProxy):
                self.proxylist.append((mydict, lastkey))

        def get_result(self, token):
            if token is not None:
                token[-1].proxylist.extend(self.proxylist)
            self.proxylist[:] = []
            return self

    @classmethod
    def parse_unquoted_str(cls, token, unicode=unicode):
        s = token[2]
        if token[1] != '=' and (s.startswith('@') or '$' in s):
            return MacroProxy(token)
        return unicode(s, 'utf-8')

loads = RsonMacros.dispatcher_factory()

if __name__ == '__main__':
    test1 = '''
fnames: []
    $firstname
    ignore me
    $(fnames[4]).txt
    ignore me too
    $lastname
foobar: @$fnames[2]
messages:
    {}
        stream: sys.stderr
        message: Welcome
    {}
        stream : $messages[0].stream
        message: Bienvenue
lastname: foobar
firstname: whoknows
bash_fragment =

    if [ -z "$debian_chroot" ] && [ -r /etc/debian_chroot ]; then
        debian_chroot=$(cat /etc/debian_chroot)
    fi

    '''
    print loads(test1)
