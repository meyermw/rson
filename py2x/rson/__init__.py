
################################################################################
####  NOTE:  THIS IS STILL IN DEVELOPMENT:                                  ####
####                                                                        ####
####    - No encoder                                                        ####
####    - = not yet implemented                                             ####
####    - Needs more tests!                                                 ####
####                                                                        ####
################################################################################

'''
RSON -- readable serial object notation

RSON is a superset of JSON with relaxed syntax for human readability.

Simple usage example:
            import rson
            obj = rson.loads(source)

Additional documentation available at:

http://code.google.com/p/rson/
'''

__version__ = '0.02'

__author__ = 'Patrick Maupin <pmaupin@gmail.com>'

__copyright__ = '''
Copyright (c) 2010, Patrick Maupin.  All rights reserved.

 Permission is hereby granted, free of charge, to any person
 obtaining a copy of this software and associated documentation
 files (the "Software"), to deal in the Software without
 restriction, including without limitation the rights to use,
 copy, modify, merge, publish, distribute, sublicense, and/or sell
 copies of the Software, and to permit persons to whom the
 Software is furnished to do so, subject to the following
 conditions:

 The above copyright notice and this permission notice shall be
 included in all copies or substantial portions of the Software.

 THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
 EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
 OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
 NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
 HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
 WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
 FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
 OTHER DEALINGS IN THE SOFTWARE.
 '''

# RSON is developed using multiple modules, but released as a single module

try:
    from rson.rson_single import *
    print '\n*** Using single file version of RSON ***\n'
except:
    from rson.tokenizer import Tokenizer, RSONDecodeError
    from rson.unquoted import UnquotedToken
    from rson.doublequoted import QuotedToken
    from rson.equals import EqualToken
    from rson.dispatcher import Dispatcher
    from rson.baseobjects import BaseObjects
    from rson.parser import RsonParser

    class RsonSystem(RsonParser, UnquotedToken, QuotedToken, EqualToken, Dispatcher, BaseObjects):
        Tokenizer = Tokenizer

    loads = RsonSystem.dispatcher_factory()
