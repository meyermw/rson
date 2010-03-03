import unittest

def all_tests_suite():
    suite = unittest.TestLoader().loadTestsFromNames([
        'rson.tests.test_sjson',
    ])
    
    return unittest.TestSuite(suite)

def main():
    runner = unittest.TextTestRunner()
    suite = all_tests_suite()
    runner.run(suite)

if __name__ == '__main__':
    import os
    import sys
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    main()
