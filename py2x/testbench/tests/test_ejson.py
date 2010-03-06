from unittest import TestCase
import os
from json import loads as sysloads
from rson.ejson import loads as newloads


class TestEJson(TestCase):

    def test_ejson(self):
        sourcedir = os.path.join(os.path.dirname(__file__), '..', 'styles')
        strings = [open(os.path.join(sourcedir, x), 'rb').read() for x in os.listdir('styles') if x.endswith('json')]

        for s in strings:
            self.assert_(sysloads(s) == newloads(s))
