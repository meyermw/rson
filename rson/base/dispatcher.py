'''
Parser dispatcher mix-in class.

Copyright (c) 2010, Patrick Maupin.  All rights reserved.

See http://code.google.com/p/rson/source/browse/trunk/license.txt
'''

def _alter_attributes(cls, attrs):
    ''' Return a new class with altered attributes.
        But throw an exception unless altered attributes
        already exist in class.
    '''
    if not attrs:
        return cls

    class Altered(cls):
        pass

    extra = cls.allowed_extra_attributes
    for name, value in attrs.items():
        if not hasattr(cls, name) and name not in extra:
            raise AttributeError('Class %s has no attribute %s'
                                        % (cls.__name__, name))
        if value is not None:
            setattr(Altered, name, staticmethod(value))
    return Altered


class Dispatcher(object):
    ''' Assumes that this is mixed-in to a class with an
        appropriate parser_factory() method.

        The design of RSON allows for many things to be replaced
        at run-time.  To support this without sacrificing too much
        efficiency, closures are used inside the classes.

        All the closures are invoked from inside the parser_factory
        method.  This class has a dispatcher_factory that decides
        when to invoke the closures based on whether the particular
        variant has been cached or not.
    '''

    allowed_extra_attributes = ()

    @classmethod
    def dispatcher_factory(cls, tuple=tuple, sorted=sorted, **kw):

        def loads(s, **kw):
            if not kw:
                return default_loads(s)

            key = tuple(sorted(kw.items()))
            func = cached(key)
            if func is None:
                func = _alter_attributes(cls, kw)().parser_factory()
                parsercache[key] = func

            return func(s)

        cls = _alter_attributes(cls, kw)
        default_loads = cls().parser_factory()
        parsercache = {}
        cached = parsercache.get
        loads.customize = cls.dispatcher_factory
        return loads
