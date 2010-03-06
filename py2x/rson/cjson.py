'''
"compatible" JSON syntax -- designed to be able to test
tokenizer/parser pieces with simplejson testsuite.

Copyright (c) 2010, Patrick Maupin.  All rights reserved.

See http://code.google.com/p/rson/source/browse/#svn/trunk/license.txt
'''

from rson.ejson import EJsonParser
from rson.unquoted import CompatibleUnquotedToken
from rson.doublequoted import QuotedToken
from rson.dispatcher import Dispatcher

class CJsonSystem(EJsonParser, CompatibleUnquotedToken, QuotedToken, Dispatcher):
    cachestrings = True
    allow_trailing_commas = False

loads = CJsonSystem.dispatcher_factory()
