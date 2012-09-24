# Deal with Python2/3 differences


try:
    unicode = unicode
except NameError:
    unicode = str
    class special_unicode(object): pass
    to_unicode = lambda token, s: s
    to_unicode2 = lambda token: token[2]
else:
    special_unicode = unicode
    to_unicode = lambda token, s, unicode=unicode: unicode(s, 'utf-8')
    to_unicode2 = lambda token, unicode=unicode: unicode(token[2], 'utf-8')

try:
    unichr = unichr
except NameError:
    unichr = chr

try:
    basestring = basestring
except NameError:
    basestring = str

try:
    next = next
except:
    next = lambda x: x.next()
