from unittest import TestCase
import os
import sys
from rson.tests.read_samples import data as samples

def strip_comments(text):
    for line in text.splitlines(True):
        l1 = line.lstrip()
        if l1 and not l1.startswith('#'):
            yield line


class TestTokenizer(TestCase):

    def setUp(self):
        from rson.base import Tokenizer
        self.t = Tokenizer.factory()
        self.delimiters = Tokenizer.delimiterset
        self.delimiters2 = self.delimiters | set('@')
        self.delimiters3 = self.delimiters | set('\n')

    def basic_check(self, s):
        def check(value, msg, *params):
            if not value:
                if params:
                    msg = msg % params
                msg = 'Error: %s:\n     %s\n' % (msg, token)
                self.assert_(0, msg)

        delimiters = self.delimiters
        delimiters2 = self.delimiters2
        delimiters3 = self.delimiters3
        tokens = self.t(s, self)

        s2 = s.replace('\r\n', '\n').replace('\r', '\n')
        #print repr(s2)
        self.assert_(tokens.source == s2)
        s2 = ''.join(strip_comments(s2)).rstrip('\n')
        #print repr(s2)
        result = []
        offset = 1
        linenum = 0
        for token in reversed(tokens):
            #print token, offset
            toffset, t0, ttext, whitespace, tindentation, tlinenum, backref = token
            tlinenum -= t0 == '@'
            newline = linenum != tlinenum
            if newline:
                check(tlinenum > linenum, 'Invalid line number')
                if tlinenum > linenum + 1 or t0 == '@':
                    check(toffset < offset, 'Invalid offset change')
                    offset = toffset
                else:
                    offset -= len(tindentation)

                linenum = tlinenum
                indentation = tindentation
                result.append(indentation)

            check(toffset == offset, 'Expected offset %s', offset)
            check(backref is tokens, 'Unexpected backref')
            check(tindentation is indentation or t0 == '@', 'Unexpected indentation')
            combined = ttext + whitespace
            result.append(combined)
            offset -= len(combined)
            check('\n' not in combined, 'Unexpected linefeed')
            check(not whitespace.strip(), 'Whitespace not white')

            if t0 in delimiters2:
                check(ttext == t0, 'Invalid delimiter')
            elif t0 == 'X':
                check(ttext.strip() == ttext, 'unstripped token')
                check(not (set(ttext) & delimiters3), 'Invalid character in text token')
            elif t0 == '\t':
                check(not ttext.strip() and not ttext.startswith(' '), 'invalid whitespace token')
                check(result[-2].startswith('\n'), 'Invalid whitespace token location')
            elif t0 == '"':
                if not ttext.endswith('"'):
                    check(not (set(ttext) & delimiters3), 'Invalid character in string token')
            elif t0 == '#':
                check(not newline, 'Unstripped comment')
            else:
                check(0, 'Unexpected token type')

        # remove final @ and initial \n
        result.pop()
        result[0] = result[0][1:]
        r2 = ''.join(result)
        #print repr(r2)
        #print repr(s2)
        self.assert_(r2 == s2)
        return tokens

    def test_simple(self):
        self.basic_check('x==y\nz:37')
        map(self.basic_check, samples)
