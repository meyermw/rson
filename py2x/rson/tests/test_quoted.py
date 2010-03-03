from unittest import TestCase
import os
import sys
from read_samples import data as samples

# Really basic test to start with -- add more later

# TODO: Add \u tests for sure...

def expected(s):
    s = s[1:-1]
    return s.replace('\\n', '\n')
    return s[1:-1]

class TestQuoted(TestCase):

    def setUp(self):
        from rson.tokenizer import Tokenizer
        self.t = Tokenizer.factory()
        from rson.doublequoted import QuotedToken
        self.q = QuotedToken.factory()

    def test_simple(self):
        tests = '''  "a" "" "abc" "abc\\n\\ndef'''.replace(' ', '\n')
        tokens = list(reversed(self.t(tests, self)))
        tokens.pop()

        a = map(self.q, tokens)
        b = map(expected, tests.split())
        print '***'
        print a
        print b
        self.assert_(a == b)
        