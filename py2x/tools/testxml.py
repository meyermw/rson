#!/usr/bin/env python
'''
A simple test of toxml

Copyright (c) 2010, Patrick Maupin.  All rights reserved.

See http://code.google.com/p/rson/source/browse/trunk/license.txt

'''

from toxml import rson2xml

source = r'''

# Comments can be used, but are not kept.

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
       special chars without an equal sign or triple quote.

   More text inside root element.

   Yetanothertag
       Note the colon is optional if you indent.

       ANIndentedTag:
           Text inside ANIndentedTag
           = Lots of text here, all together in a block.
             Can have special characters like \[]{},:"=
             if I want them.

             Blank lines embedded in the block are kept,
             but blank lines at the end are not.


           # Attribute for indented tag could be anywhere
           # at the same indentation level.

           {att1:whatever}
           {att2: something else}
           {}
               att3: Lots of ways to provide attributes
               att4: if you feel you really need them
           {att5: "but really, do you?  That's the question"}
       """ I can also use triple-quoted strings
if I want weird data. """
       "And, of course, I can use JSON double-quoted strings"

   ATagWithOnlyAttributes:
       {HereIsAnAttr: and a value, AndAnother: value too}

   FinalTag:  Indentation is optional if you use a colon
'''

dest = r'''

<root attribute1="hi" attribute2="there">
    Some text inside the root element.
    <othertag>
        Just text here -- could be multiple lines but no
        special chars without an equal sign or triple quote.
    </othertag>
    More text inside root element.
    <Yetanothertag>
        Note the colon is optional if you indent.
        <ANIndentedTag att1="whatever" att2="something else" att3="Lots of ways to provide attributes" att4="if you feel you really need them" att5="but really, do you?  That's the question">
            Text inside ANIndentedTag
            Lots of text here, all together in a block.
            Can have special characters like \[]{},:"=
            if I want them.

            Blank lines embedded in the block are kept,
            but blank lines at the end are not.
        </ANIndentedTag>
         I can also use triple-quoted strings
        if I want weird data.
        And, of course, I can use JSON double-quoted strings
    </Yetanothertag>
    <ATagWithOnlyAttributes HereIsAnAttr="and a value" AndAnother="value too"/>
    <FinalTag>
        Indentation is optional if you use a colon
    </FinalTag>
</root>

'''

answer = str(rson2xml(source))

print answer

answer = [x.rstrip() for x in answer.strip().splitlines()]
dest = [x.rstrip() for x in dest.strip().splitlines()]

assert answer == dest
