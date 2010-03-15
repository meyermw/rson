#!/usr/bin/env python
'''
A simple test of the toxml module, which allows extended RSON
syntax to be used to create XML.

This module contains some RSON, and the corresponding XML.  Executing
the module verifies they are the same.

Copyright (c) 2010, Patrick Maupin.  All rights reserved.

See http://code.google.com/p/rson/source/browse/trunk/license.txt

'''

from toxml import rson2xml

source = r'''

# Comments can be used, but are not kept when the XML is generated.

# In general, blank lines are meaningless, except when inside a
# triple-quoted or equal delimited string block.

# XML syntax requires a single tag at the top of the file.  We'll
# call it root:

root:

   # Attribute blocks are inside JSON-style dictionaries
   # or using the extended syntax that allows you to
   # make an empty dict, then fill it.
   {}
      attribute1: hi
      attribute2: there

   # Unquoted text is allowed, but cannot have \{}[],:=
   # Unquoted text could have ", but not at first character

   Some text inside the root element.

   othertag:
       Just text here -- could be multiple lines but no
       special chars without quoting or using an equal sign.

   Some more text inside the root element.

   Yetanothertag
       Note the colon after the tag is optional if you indent.

       AMoreIndentedTag:

           This text is inside AMoreIndentedTag

           # The equal sign starts a text block.  The text block
           # continues until we unindent to the level of the
           # equal sign (or even farther left).

           = Lots of text here, all together in a block.
             Can have special characters like \[]{},:"=
             if I want them.

             Blank lines embedded in the block are kept,
             but blank lines at the end are not.


           # Attribute for indented tag could be anywhere
           # at the same indentation level as the rest of
           # the data inside the tag.  Also, they do not
           # all need to be declared together.

           {att1:whatever}
           {att2: something else}
           {}
               att3: Lots of ways to provide attributes
               att4: if you feel you really need them
           {att5: "but really, do you?  That's the question"}


       """I can also use triple-quoted strings,
if I want weird characters inside my data.  With triple-quoted strings, the
only escaping that occurs is that \\""" has the \ removed from the front of it. """

       "And, of course, I can use JSON double-quoted strings for all sorts of character escapes."

       = XML special characters like &, <, and > are no problem, either.
         (I just put them inside the equal block quote because the comma is an
          RSON delimiter character.)  Here, I'll show them without any quoting whatsoever:

       & < >


   ATagWithOnlyAttributes:
       {HereIsAnAttr: and a value, AndAnother: value too}
       {EscapeQuotes: " I said \"Hi!\""}

   TinyTag: On a single line.
   FinalTag:  Indentation is optional if you use a colon.
'''

dest = r'''

<root attribute1="hi" attribute2="there">
    Some text inside the root element.
    <othertag>
        Just text here -- could be multiple lines but no
        special chars without quoting or using an equal sign.
    </othertag>
    Some more text inside the root element.
    <Yetanothertag>
        Note the colon after the tag is optional if you indent.
        <AMoreIndentedTag att1="whatever" att2="something else" att3="Lots of ways to provide attributes" att4="if you feel you really need them" att5="but really, do you?  That's the question">
            This text is inside AMoreIndentedTag
            Lots of text here, all together in a block.
            Can have special characters like \[]{},:"=
            if I want them.

            Blank lines embedded in the block are kept,
            but blank lines at the end are not.
        </AMoreIndentedTag>
        I can also use triple-quoted strings,
        if I want weird characters inside my data.  With triple-quoted strings, the
        only escaping that occurs is that \""" has the \ removed from the front of it.
        And, of course, I can use JSON double-quoted strings for all sorts of character escapes.
        XML special characters like &amp;, &lt;, and &gt; are no problem, either.
        (I just put them inside the equal block quote because the comma is an
         RSON delimiter character.)  Here, I'll show them without any quoting whatsoever:
        &amp; &lt; &gt;
    </Yetanothertag>
    <ATagWithOnlyAttributes HereIsAnAttr="and a value" AndAnother="value too" EscapeQuotes=' I said "Hi!"'/>
    <TinyTag>On a single line.</TinyTag>
    <FinalTag>
        Indentation is optional if you use a colon.
    </FinalTag>
</root>

'''

answer = str(rson2xml(source))

print answer

answer = [x.rstrip() for x in answer.strip().splitlines()]
dest = [x.rstrip() for x in dest.strip().splitlines()]

assert answer == dest
