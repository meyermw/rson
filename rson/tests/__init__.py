#!/usr/bin/env python

import os
import sys
import unittest

ismain = __name__ == '__main__'

root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

if ismain:
    sys.path.insert(0, root)

# I dunno why, but I have to do this for Python3
import rson.tests.test_tokenizer
import rson.tests.test_unquoted
import rson.tests.test_quoted
import rson.tests.test_parser


def all_tests_suite():
    suite = unittest.TestLoader().loadTestsFromNames([
        'rson.tests.test_tokenizer',
        'rson.tests.test_unquoted',
        'rson.tests.test_quoted',
        'rson.tests.test_parser',
    ])

    return unittest.TestSuite(suite)

def simple_json_tests():
    sjroot = os.path.join(os.path.dirname(root), 'simplejson')
    sys.path[0:0] = sjroot + str(sys.version_info[0]), sjroot
    try:
        import simplejson
        import simplejson.tests
        import rson
        import rson.pyjson
    except ImportError:
        print('Could not load simplejson tests')
        return

    simplejson.loads = rson.pyjson.loads
    simplejson.JSONDecodeError = rson.RSONDecodeError
    simplejson.tests.main()

def main(try_simple_json=True):
    runner = unittest.TextTestRunner()
    suite = all_tests_suite()
    runner.run(suite)
    if try_simple_json:
        simple_json_tests()

if ismain:
    main()
