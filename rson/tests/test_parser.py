from unittest import TestCase
import os
from json import loads as sysloads
from rson import loads as newloads

from rson.py23 import basestring

rootdir = os.path.dirname(__file__)

class TestParser(TestCase):

    def test_parser(self):
        sourcedir = os.path.join(rootdir, 'styles')
        strings = [open(os.path.join(sourcedir, x), 'rb').read() for x in os.listdir(sourcedir) if x.endswith('json')]

        for s in strings:
            s2 = s
            if not isinstance(s, basestring):
                s2 = s.decode('utf-8', 'replace')

            self.assert_(sysloads(s2) == newloads(s))

    def test_rson_vs_json(self):
        result = []
        fnames = (os.path.join(rootdir, 'styles', 'styles.json'),
                  os.path.join(rootdir,'styles.rson'))
        for fname in fnames:
            text = open(fname, 'rb').read()
            data = newloads(text)
            data['styles'] = dict(data['styles'])
            result.append(data)
        self.assertEquals(*result)

    def test_python_syntax(self):
        ''' Test a limited subset of Python syntax,
            after modifying "=" to be ":".
            Also, this is probably the easiest way to
            test triple quote processing.
        '''
        teststr = '''

# Comment goes here

x = 27
y = [1, 2, 3, {"z": 42}]


    # Although comments cannot go after other data,
    # they can be arbitrarily indented.

m = """
Now is the time for all good men
to come to the aid of their country.
"""

w = ["""test""",
     """triple""",
     {"""quotes""":"ok?"}]

num1 = 0x100
num2 = 0b101010
num3 = 0o455
num5 = 0.1
num6 = 01.2
num7 = .2

'''
        testdict = {}
        try:
            exec(teststr, testdict)
        except:
            exec('exec teststr in testdict')

        del testdict['__builtins__']

        self.assertEquals(testdict, newloads(teststr.replace('=', ':')))


    def test_various(self):
        ae, l = self.assertEquals, newloads
        data = r'''

        'a:[]\n x', {'a':['x']}

        # Non-string keys not supported by default
        #'[a,b]:[c,d]', {('a','b'):['c', 'd']}
        #'{[a,b]:[1,2,3], 0:1}:[c,d]', {((0, 1), (('a', 'b'), (1, 2, 3)),):['c', 'd']}
        #'[]\n a\n b', ['a', 'b']
        #'[]:[]:[]', {():{():[]}}

        'a:b\n c', {'a': {'b': 'c'}}

        'a:b\n c\n d', {'a': {'b': ['c', 'd']}}

        '[]', []

        '[]\n []\n  []',      [[[]]]
        '[]\n []\n  []\n a',  [[[]], 'a']
        '[]\n []\n  []\n {}', [[[]], {}]
        '[]\n []\n  []\n {}\n  a\n   b', [[[]], {'a':'b'}]

        'a:b:c\n d:e\n f:g\na:b:w\n z:x', {'a': {'b': {'c': {'d': 'e', 'f': 'g'}, 'w': {'z': 'x'}}}}

        'a: = Hi there, how are you?', {'a': 'Hi there, how are you?'}
        'a = Hi there, how are you?', {'a': 'Hi there, how are you?'}
        'a =Hi there, how are you?', {'a': 'Hi there, how are you?'}
        'a =  Hi there, how are you?', {'a': 'Hi there, how are you?'}
        'a =  \n Hi there, how are you?\n   \n   \n   ', {'a': 'Hi there, how are you?\n'}


        '=1\n=2\n3', [1, 2, 3]
        '=\n 1\n=\n 2\n3', ['1\n', '2\n', 3]

        '{}\n x:7\nx', [{'x':7}, 'x']

        '''
        data = [x.strip() for x in data.splitlines()]
        data = [x for x in data if x and not x.startswith('#')]
        for line in data:
            s, r = eval(line)
            ae(l(s), r)

'''
Failures -- add tests
        '[]\n a\n  b'

'''
