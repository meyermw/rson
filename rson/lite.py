'''
rson.lite attempts to match rsonlite capabilities with full-blown rson.

Copyright (c) 2010, Patrick Maupin.  All rights reserved.

See http://code.google.com/p/rson/source/browse/trunk/license.txt

Differences between rson.lite and rsonlite:

    1)  rson.lite will raise an exception if passed an empty string.
        rsonlite will return an empty array.

    2) The exception returned on invalid indentation is different,
       because rsonlite reuses standard IndentationError.

    3) The whitespace at beginning and end of multi-line strings may
       sometimes differ slightly.

    4) The '#' character can appear inside a key string in rson.lite,
       but always starts a comment when it isn't inside a '=' string
       in rsonlite.
'''

from rson import loads as base_loads
from rson.py23 import basestring

# Use OrderedDict if it's available
try:
    from collections import OrderedDict as stddict
except ImportError:
    stddict = dict

loads = base_loads.customize(
    user_defined_unquoted=True,
    disallow_missing_object_keys = False,
    disallow_multiple_object_keys = True,
    create_raw_objects = True,
    disallow_rson_sublists = True,
    disallow_rson_subdicts = True,
    rson_subelement_delimiter = None,
    rson_quote_delimiter = None,
)

def dumps(data, indent='    ', initial_indent=''):
    ''' Dump a string loaded with loads back out.
    '''
    def getstring(data, indent2):
        if '\n' in data:
            data = ('\n'+indent2).join([''] + data.split('\n'))
        return data

    def recurse(data, indent2):
        assert isinstance(data, list), repr(data)
        for data in data:
            if isinstance(data, tuple):
                key, value = data
                if len(value) == 1 and isinstance(value[0], basestring):
                    append('%s%s = %s' % (indent2, key, getstring(value[0], indent2+indent)))
                else:
                    append('%s%s' % (indent2, key))
                    recurse(value, indent2 + indent)
            else:
                assert isinstance(data, basestring)
                if '\n' in data or '=' in data or '#' in data:
                    append(indent2 + '=')
                    append(getstring(data, indent2 + '    '))
                else:
                    append('%s%s' % (indent2, data))
    result = []
    append = result.append
    recurse(data, initial_indent)
    append('')
    return '\n'.join(result)

def pretty(data, indent='    '):
    ''' Pretty-print a string loaded by loads into
        something that makes it easy to see the actual
        structure of the data.  The return value of
        this should be parseable by eval()
    '''
    def recurse(data, indent2):
        assert isinstance(data, list)
        for data in data:
            assert isinstance(data, (tuple, basestring))
            if isinstance(data, tuple) and (
                       len(data[1]) != 1 or not isinstance(data[1][0], basestring)):
                append('%s(%s, [' % (indent2, repr(data[0])))
                recurse(data[1], indent2 + indent)
                append('%s])' % (indent2))
            else:
                append('%s%s,' % (indent2, repr(data)))
    result = []
    append = result.append
    append('[')
    recurse(data, indent)
    append(']')
    append('')
    return '\n'.join(result)

##########################################################################
# These higher-level functions might suffice for simple data, and also
# provide a template for designing similar functions.

def stringparse(s, special=dict(true=True, false=False, null=None)):
    ''' This gives an example of handling the JSON special identifiers
        true, false and null, and also of handling simple arrays.
    '''
    if s in special:
        return special[s]
    if s.startswith('[') and s.endswith(']'):
        t = s[1:-1]
        for ch in '"\'[]{}\n':
            if ch in t:
                return s
        return [x.strip() for x in t.split(',')]
    return s

def simpleparse(source, stringparse=stringparse, stddict=stddict):
    ''' Return the simplest structure that uses dicts instead
        of tuples, and doesn't lose any source information.
        Use ordered dicts if they are available.
    '''
    def recurse(mylist):
        if len(mylist) == 1 and isinstance(mylist[0], basestring):
            return stringparse(mylist[0])
        keys = [x[0] for x in mylist if isinstance(x, tuple)]
        if not keys:
            return mylist  # simple list
        if len(set(keys)) == len(mylist):
            return stddict((x, recurse(y)) for (x, y) in mylist)
        # Complicated.  Make a list that might have multiple dicts
        result = []
        curdict = None
        for item in mylist:
            if not isinstance(item, tuple):
                result.append(stringparse(item))
                curdict = None
                continue
            key, value = item
            if curdict is None or key in curdict:
                curdict = stddict()
                result.append(curdict)
            curdict[key] = recurse(value)
        return result
    return recurse(source if isinstance(source, list) else loads(source))
