import unittest

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

def main():
    runner = unittest.TextTestRunner()
    suite = all_tests_suite()
    runner.run(suite)
