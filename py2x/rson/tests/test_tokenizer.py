from unittest import TestCase
import os
import sys


class TestTokenizer(TestCase):

    def setUp(self):
        from rson.tokenizer import Tokenizer
        self.t = Tokenizer.factory()

    def basic_check(self, s):
        tokens = self.t(s, self)
        s2 = s.replace('\r\n', '\n').replace('\r', '\n')
        self.assert_(tokens.source == s2)
        result = []
        offset = 1
        linenum = 0
        for token in reversed(tokens):
            #print token, offset
            toffset, t0, ttext, whitespace, tindentation, tlinenum, client = token
            if linenum != tlinenum:
                self.assert_(tlinenum == linenum + 1)
                linenum = tlinenum
                indentation = tindentation
                result.append(indentation)
                offset -= len(indentation)
            self.assert_(toffset == offset)
            self.assert_(client is self)
            offset -= len(ttext) + len(whitespace)
            self.assert_(tindentation is indentation or t0 == '@')
            result.append(ttext)
            result.append(whitespace)

        # remove final @ and initial \n
        result[-2:] = []
        result[0] = result[0][1:]
        r2 = ''.join(result)
        self.assert_(r2 == s2)
        return tokens

    def test_simple(self):
        self.basic_check('x==y\nz:37')
