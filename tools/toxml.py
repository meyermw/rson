#!/usr/bin/env python
'''
An example script for RSON that generates XML from source text using the RSON
parser.

This could use a bit better error reporting, etc. but is basically functional.

Copyright (c) 2010, Patrick Maupin.  All rights reserved.

See http://code.google.com/p/rson/source/browse/trunk/license.txt

'''


import sys
sys.path.insert(0, '..')
from rson import RsonSystem

from xml.sax.saxutils import escape, quoteattr

def xml_dispatcher_factory():

    class RsonObject(list):
        ''' This object is used by rson when parsing, rather than the
            usual dict inside rson.  Just maintains things in a list.
            isinstance() is used to distinguish between this and a regular list.
        '''
        def get_result(self, token):
            self.token = token
            return self
        def error(self, msg):
            token = self.token
            token[-1].error(msg, token)
        def __repr__(self):
            return 'RsonObj(%s)' % ', '.join('Item(%s)' % x for x in self)

    class RsonXml(RsonSystem):
        ''' We subclass the rson parser, making a few changes to support
            our XML syntax and semantics.
        '''

        # This change allows mixing single values and key/value pairs at
        # the same indentation level.  We use the key/value pairs for
        # nested elements, and single values as either text or as attribute
        # dictionaries, depending on the element type.

        disallow_missing_object_keys = False

        # This change disables the normal rson parsing which allows
        # key1 : key2 : key3 .... : keyn : value to build nested dicts.

        disallow_multiple_object_keys = True

        # This change requires that keys be strings.

        disallow_nonstring_keys = True

        # This change doesn't use [] as special tokens

        disallow_rson_sublists = True

        # This change uses our object instead of the default built-in one
        default_object = RsonObject

        # This change treats all unquoted tokens as strings (no special
        # casing for numbers, true, false, null).

        def unquoted_parse_factory(self, unicode=unicode):
            def parse(token, next):
                return unicode(token[2], 'utf-8')
            return parse


    class XmlObject(list):
        ''' Each instance of this object represents a node in the XML tree.
            __init__ is passed parse-tree data from rson, and will recursively
            create the XML sub-objects.
        '''
        def __init__(self, data):
            tag, data = data
            assert isinstance(tag, basestring)
            if not isinstance(data, RsonObject):
                assert isinstance(data, basestring)
                data = [[data]]
            self.tag = tag
            self.attr = attrlist = []
            for item in data:
                if len(item) == 1:
                    item = item[0]
                    if isinstance(item, basestring):
                        self.append(escape(item))
                    else:
                        assert isinstance(item, RsonObject)
                        attrlist.extend(item)
                else:
                    self.append(XmlObject(item))


        def __str__(self):
            ''' A reasonably brain-dead object dumper
            '''
            tag = self.tag
            attr = ['%s=%s' % (x, quoteattr(y)) for (x,y) in self.attr]
            header = [tag] + attr
            header = ' '.join(header)
            if not self:
                return '<%s/>' % header
            data = [str(x) for x in self]
            if len(data) == 1 and len(data[0]) <= 40 and '\n' not in data[0]:
                return '<%s>%s</%s>' % (header, data[0], tag)
            data.insert(0, '<%s>' % header)
            data = [x.rstrip() for x in data]
            data = '\n'.join(data).replace('\n', '\n    ')
            return '%s\n</%s>' % (data, tag)

    loads = RsonXml.dispatcher_factory()


    def convert(s):
        ''' Use our modified loads to read the data in, then convert it
            to an XML tree and return the tree.
        '''
        tree = loads(s)
        assert isinstance(tree, RsonObject)
        if len(tree) != 1:
            tree.error('More than one root node: [%s]' % ', '.join(x[0] for x in tree))
        return XmlObject(tree[0])

    return convert

rson2xml = xml_dispatcher_factory()

def rsonf2xmlf(srcf, dstf):
    f = open(srcf, 'rb')
    data = f.read()
    f.close()

    data = rson2xml(data)

    f = open(dstf, 'wb')
    f.write(str(data))
    f.close()

if __name__ == '__main__':
    try:
        srcf, dstf = sys.argv[1:]
    except:
        raise SystemError('''
toxml converts an enhanced rson file into xml.

usage:

    toxml.py <sourcef> <dstf>
''')

    rsonf2xmlf(srcf, dstf)

