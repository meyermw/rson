'''
A part of rson.

Additional documentation available at:

http://code.google.com/p/rson/
'''

from rson.base.tokenizer import Tokenizer, RSONDecodeError
from rson.base.unquoted import UnquotedToken
from rson.base.doublequoted import QuotedToken
from rson.base.equals import EqualToken
from rson.base.dispatcher import Dispatcher
from rson.base.baseobjects import BaseObjects
from rson.base.parser import RsonParser

class RsonSystem(RsonParser, UnquotedToken, QuotedToken, EqualToken, Dispatcher, BaseObjects):
    Tokenizer = Tokenizer

loads = RsonSystem.dispatcher_factory()
