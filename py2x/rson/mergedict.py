'''
Mergeable dictionary for RSON

Copyright (c) 2010, Patrick Maupin.  All rights reserved.

See http://code.google.com/p/rson/source/browse/#svn/trunk/license.txt

STILL A WORK IN PROGRESS!!!!!!!

'''

class MergeDict(object):

    @staticmethod
    def dict_factory(isinstance=isinstance, dict=dict, ValueError=ValueError):

        class EasyDict(dict):
            ''' A dictionary class with easy attribute access in many cases.
            '''

        def merge(source):
            result = EasyDict()
            for itemlist in source:
                mydict = result
                try:
                    key, value = itemlist
                except ValueError:
                    for key in itemlist[:-2]:
                        subdict = mydict.get(key)
                        if not isinstance(subdict, dict):
                            subdict = mydict[key] = EasyDict()
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
