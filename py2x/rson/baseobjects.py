'''
Base objects (list and dict) for RSON

Copyright (c) 2010, Patrick Maupin.  All rights reserved.

See http://code.google.com/p/rson/source/browse/#svn/trunk/license.txt

'''

class BaseObjects(object):

    class base_dict(dict):
        ''' A replaceable dictionary class with easy
            attribute access in many cases.
        '''
        def __getattr__(self, name):
            self.__dict__ = self
            return self[name]

    def dict_factory(self, isinstance=isinstance, dict=dict, hash=hash,
                            tuple=tuple, sorted=sorted, ValueError=ValueError):

        base_dict = self.base_dict

        def make_hashable(what):
            try:
                hash(what)
                return what
            except TypeError:
                if isinstance(what, dict):
                    return tuple(sorted(make_hashable(x) for x in what.iteritems()))
                return tuple(make_hashable(x) for x in what)

        def merge(source):
            result = base_dict()
            for itemlist in source:
                mydict = result
                value = itemlist.pop()
                itemlist = [make_hashable(x) for x in itemlist]
                lastkey = itemlist.pop()

                if itemlist:
                    itemlist.reverse()
                    while itemlist:
                        key = itemlist.pop()
                        subdict = mydict.get(key)
                        if not isinstance(subdict, dict):
                            subdict = mydict[key] = base_dict()
                        mydict = subdict
                if isinstance(value, dict):
                    oldvalue = mydict.get(lastkey)
                    if isinstance(oldvalue, dict):
                        oldvalue.update(value)
                        continue
                mydict[lastkey] = value
            return result

        return merge
