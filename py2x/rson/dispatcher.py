'''
Parser dispatcher mix-in class.

Copyright (c) 2010, Patrick Maupin.  All rights reserved.

See http://code.google.com/p/rson/source/browse/trunk/license.txt
'''

class Dispatcher(object):
    ''' Assumes that this is mixed-in to a class with an
        appropriate parser_factory() method.
    '''

    @classmethod
    def dispatcher_factory(cls, hasattr=hasattr, tuple=tuple, sorted=sorted):

        self = cls()
        parser_factory = self.parser_factory
        parsercache = {}
        cached = parsercache.get
        default_loads = parser_factory()

        def loads(s, **kw):
            if not kw:
                return default_loads(s)

            key = tuple(sorted(kw.items()))
            func = cached(key)
            if func is None:
                # Begin some real ugliness here -- just modify our instance to
                # have the correct user variables for the initialization functions.
                # Seems to speed up simplejson testcases a bit.
                self.__dict__ = dict((x,y) for (x,y) in key if y is not None)
                func = parsercache[key] = parser_factory()

            return func(s)

        return loads
