import unittest

def all_tests_suite():
    suite = unittest.TestLoader().loadTestsFromNames([
        'tests.test_tokenizer',
        'tests.test_unquoted',
        'tests.test_quoted',
        'tests.test_parser',
    ])

    return unittest.TestSuite(suite)

def main():
    runner = unittest.TextTestRunner()
    suite = all_tests_suite()
    runner.run(suite)
