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

    def dict_factory(self, isinstance=isinstance, dict=dict,
                                 ValueError=ValueError):

        base_dict = self.base_dict

        def merge(source):
            result = base_dict()
            for itemlist in source:
                mydict = result
                try:
                    key, value = itemlist
                except ValueError:
                    for key in itemlist[:-2]:
                        subdict = mydict.get(key)
                        if not isinstance(subdict, dict):
                            subdict = mydict[key] = base_dict()
                        mydict = subdict
                    key, value = itemlist[-2:]
                if isinstance(value, dict):
                    oldvalue = mydict.get(key)
                    if isinstance(oldvalue, dict):
                        oldvalue.update(value)
                        continue
                mydict[key] = value
            return result

        return merge
