'''
Base objects (list and dict) for RSON

Copyright (c) 2010, Patrick Maupin.  All rights reserved.

See http://code.google.com/p/rson/source/browse/#svn/trunk/license.txt

'''

class BaseObjects(object):

    # These hooks allow compatibility with simplejson
    object_hook = None
    object_pairs_hook = None
    array_hook = None

    # Stock object constructor does not cope with no keys
    disallow_missing_object_keys = True

    # Stock object constructor copes with multiple keys just fine
    disallow_multiple_object_keys = False

    # Stock object constructor copes with non-string keys just fine
    disallow_nonstring_keys = False

    def default_array_factory(self):
        ''' This function returns a constructor for RSON arrays.
        '''
        def new_array(startlist, token):
            return startlist
        return new_array

    class default_object(dict):
        ''' By default, RSON objects are dictionaries that
            allow attribute access to their existing contents.
        '''
        def __init__(self):
            self.__dict__ = self

    def default_object_factory(self, isinstance=isinstance, dict=dict, hash=hash,
                            tuple=tuple, sorted=sorted, ValueError=ValueError):
        ''' This function returns a constructor for RSON objects (dicts).
        '''

        default_object = self.default_object

        def make_hashable(what):
            try:
                hash(what)
                return what
            except TypeError:
                if isinstance(what, dict):
                    return tuple(sorted(make_hashable(x) for x in what.iteritems()))
                return tuple(make_hashable(x) for x in what)

        def merge(source, token):
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
        ''' This function returns constructors for RSON objects and arrays.
            It handles simplejson compatible hooks as well.
        '''
        object_hook = self.object_hook
        object_pairs_hook = self.object_pairs_hook

        if object_pairs_hook is not None:
            def build_object(source, token):
                return object_pairs_hook([tuple(x) for x in source])
            self.disallow_multiple_object_keys = True
            self.disallow_nonstring_keys = True
        elif object_hook is not None:
            mydict = dict
            def build_object(source, token):
                return object_hook(mydict(source))
            self.disallow_multiple_object_keys = True
            self.disallow_nonstring_keys = True
        else:
            build_object = self.default_object_factory()

        build_array = self.array_hook or self.default_array_factory()
        return build_object, build_array
