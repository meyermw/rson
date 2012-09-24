from unittest import TestCase
import os
import sys
from rson.tests.read_samples import data as samples
from rson.py23 import unicode

# Really basic test to start with -- add more later

def expected(s):
    if s == 'true': return True
    if s == 'false': return False
    if s == 'null': return None
    try:
        return int(s.replace('_', ''), 0)
    except:
        pass
    try:
        return float(s)
    except:
        return unicode(s)


class TestUnquoted(TestCase):

    def setUp(self):
        from rson.base import Tokenizer, UnquotedToken
        self.t = Tokenizer.factory()
        self.u = UnquotedToken().unquoted_parse_factory()

    def test_simple(self):
        tests = ''' 0 0.0 false true null 1.2 -3.7e5 Hey there how ya doin? '''.replace(' ', '\n')
        tokens = list(reversed(self.t(tests, self)))
        tokens.pop()

        a = list(map(self.u, tokens, tokens))
        b = list(map(expected, tests.split()))
        self.assert_(a == b)
