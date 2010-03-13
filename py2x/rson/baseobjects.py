'''
Base objects (list and dict) for RSON

Copyright (c) 2010, Patrick Maupin.  All rights reserved.

See http://code.google.com/p/rson/source/browse/#svn/trunk/license.txt

'''

class BaseObjects(object):

    object_hook = None
    object_pairs_hook = None
    object_pairs_expects_tuple = False
    array_hook = list

    class default_object(dict):
        ''' A replaceable dictionary class with easy
            attribute access in many cases.
        '''
        def __getattr__(self, name):
            self.__dict__ = self
            return self[name]

    def default_object_factory(self, isinstance=isinstance, dict=dict, hash=hash,
                            tuple=tuple, sorted=sorted, ValueError=ValueError):

        default_object = self.default_object

        def make_hashable(what):
            try:
                hash(what)
                return what
            except TypeError:
                if isinstance(what, dict):
                    return tuple(sorted(make_hashable(x) for x in what.iteritems()))
                return tuple(make_hashable(x) for x in what)

        def merge(source):
            result = default_object()
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
                            subdict = mydict[key] = default_object()
                        mydict = subdict
                if isinstance(value, dict):
                    oldvalue = mydict.get(lastkey)
                    if isinstance(oldvalue, dict):
                        oldvalue.update(value)
                        continue
                mydict[lastkey] = value
            return result

        return merge

    def object_type_factory(self, dict=dict, tuple=tuple):
        object_hook = self.object_hook
        object_pairs_hook = self.object_pairs_hook
        if object_pairs_hook is None:
            if object_hook is None:
                object_pairs_hook = self.default_object_factory()
            else:
                mydict = dict
                object_pairs_hook = lambda x: object_hook(mydict(x))
        elif self.object_pairs_expects_tuple:
            real_object_pairs_hook = object_pairs_hook
            def object_pairs_hook(what):
                return real_object_pairs_hook([tuple(x) for x in what])

        return object_pairs_hook, self.array_hook

