from unittest import TestCase
import os
import sys
from rson.tests.read_samples import data as samples

# Really basic test to start with -- add more later

# TODO: Add \u tests for sure...

def expected(s):
    s = s[1:-1]
    return s.replace('\\n', '\n')
    return s[1:-1]

class TestQuoted(TestCase):

    def setUp(self):
        from rson.base import Tokenizer, QuotedToken
        self.t = Tokenizer.factory()
        self.q = QuotedToken().quoted_parse_factory()

    def test_simple(self):
        tests = '''  "a" "" "abc" "abc\\n\\ndef"'''.replace(' ', '\n')
        tokens = list(reversed(self.t(tests, self)))
        tokens.pop()

        a = list(map(self.q, tokens, tokens))
        b = list(map(expected, tests.split()))
        self.assert_(a == b)
