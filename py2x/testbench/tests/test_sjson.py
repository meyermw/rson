from unittest import TestCase
import os
import sys

# Probably not the best way to do this -- should clean up later

class TestSJson(TestCase):

    def test_all_simple(self):
        jsonroot = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'simplejson'))
        sys.path.insert(0, jsonroot)
        import simplejson.tests
        simplejson.tests.main()
