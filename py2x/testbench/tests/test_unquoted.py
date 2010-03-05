from unittest import TestCase
import os
import sys
from read_samples import data as samples

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
        from rson.tokenizer import Tokenizer
        self.t = Tokenizer.factory()
        from rson.unquoted import UnquotedToken
        self.u = UnquotedToken.factory()

    def test_simple(self):
        tests = ''' 0 0.0 false true null 1.2 -3.7e5 Hey there how ya doin? '''.replace(' ', '\n')
        tokens = list(reversed(self.t(tests, self)))
        tokens.pop()

        a = map(self.u, tokens, tokens)
        b = map(expected, tests.split())
        self.assert_(a == b)
