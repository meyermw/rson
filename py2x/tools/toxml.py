#!/usr/bin/env python
'''
An example script for RSON that generates XML from source text using the RSON
parser.

Copyright (c) 2010, Patrick Maupin.  All rights reserved.

See http://code.google.com/p/rson/source/browse/#svn/trunk/license.txt

'''


import sys
sys.path.insert(0, '..')
from rson import RsonSystem

from xml.sax.saxutils import escape, quoteattr

def xml_dispatcher_factory():
    class RsonObject(list):
        def __init__(self, value, token):
            self.extend(value)
            self.token = token
        def error(self, msg):
            token = self.token
            token[-1].error(msg, token)
        def __repr__(self):
            return 'RsonObj(%s)' % ', '.join('Item(%s)' % x for x in self)

    class RsonXml(RsonSystem):
        disallow_missing_object_keys = False
        disallow_multiple_object_keys = True
        disallow_nonstring_keys = True

        def default_object_factory(self):
            return RsonObject

        def unquoted_parse_factory(self, unicode=unicode):
            def parse(token, next):
                return unicode(token[2], 'utf-8')
                s = token[2]
            return parse


    class XmlObject(list):
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
        tree = loads(s)
        assert isinstance(tree, RsonObject)
        if len(tree) != 1:
            tree.error('More than one root node: [%s]' % ', '.join(x[0] for x in tree))
        return XmlObject(tree[0])

    return convert

loads = xml_dispatcher_factory()

if __name__ == '__main__':
    print loads('''
root:
   {}
      attribute1: hi
      attribute2: there
   Some text inside the root element.
   othertag:
       Just text here -- could be multiple lines but no
       special chars without an equal sign or triple quote.
   More text inside root element.
   Yetanothertag
       The colon is optional if you indent.
       ANIndentedTag:
           Text inside ANIndentedTag
           = Lots of text
             here, all together
             in a block.  Can have special characters
             if I want them.
           # Attribute for indented tag could be anywhere
           # inside the nest level
           {att1:whatever}
           {att2: something else}
   FinalTag:  Indentation is optional if you use a colon
''')
