'''
"enhanced" JSON syntax -- no indentation support, but a few other RSON features.

Copyright (c) 2010, Patrick Maupin.  All rights reserved.

See http://code.google.com/p/rson/source/browse/#svn/trunk/license.txt
'''

from rson.tokenizer import Tokenizer
from rson.unquoted import UnquotedToken
from rson.doublequoted import QuotedToken
from rson.dispatcher import Dispatcher

class EasyDict(dict):
    ''' A dictionary class with easy attribute access in many cases.
    '''
    def __init__(self, source):
        self.__dict__ = self
        self.update(source)

class EJsonParser(object):
    ''' Enhanced JSON parser

        NOTE:  This is not (and may never be) production-worthy.  It is an
               example of how to put together some of the basic parts of
               RSON, before I get the "real" parser going.

        - Comments allowed on separate lines
        - Simple strings don't have to be quoted
        - Numbers can be hex or octal or binary, and have embedded underscores
        - Allows trailing commas
    '''

    Tokenizer = Tokenizer
    object_hook = None
    object_pairs_hook = None
    _default_object_class = EasyDict
    allow_trailing_commas = True

    def parser_factory(self):

        Tokenizer = self.Tokenizer
        tokenizer = Tokenizer.factory()
        error = Tokenizer.error

        read_unquoted = self.unquoted_parse_factory()
        read_quoted = self.quoted_parse_factory()
        allow_trailing_commas = self.allow_trailing_commas

        object_hook = self.object_hook
        object_pairs_hook = self.object_pairs_hook
        if object_pairs_hook is None:
            if object_hook is None:
                object_pairs_hook = self._default_object_class
            else:
                mydict = dict
                object_pairs_hook = lambda x: object_hook(mydict(x))

        def bad_array_element(token, next):
            error('Expected array element', token)

        def bad_dict_key(token, next):
            error('Expected dictionary key', token)

        def bad_dict_value(token, next):
            error('Expected dictionary value', token)

        def bad_top_value(token, next):
            error('Expected start of object', token)

        def read_json_array(firsttok, next, entirestring=False):
            result = []
            append = result.append
            while 1:
                token = next()
                t0 = token[1]
                if t0 in ']@':
                    if result and not allow_trailing_commas:
                        error('Unexpected trailing comma', token)
                    break
                append(value_dispatch(t0,  bad_array_element)(token, next))
                delim = next()
                t0 = delim[1]
                if t0 in ',;':
                    continue

                # Allow line ending to be used as a comma, so
                # just pretend we got a comma if on a new line
                if t0 not in ']@' and token[-2] != delim[-2]:
                    token[-1].push(delim)
                    continue
                token = delim
                break

            if t0 != ']':
                if t0 != '@':
                    error('Expected "," or "]"', token)
                if not entirestring:
                    error('Unterminated list (no matching "]")', firsttok)

            return result

        def read_json_dict(token, next, entirestring=False):
            result = []
            append = result.append
            while 1:
                token = next()
                t0 = token[1]
                if t0  in '}@':
                    if result and not allow_trailing_commas:
                        error('Unexpected trailing comma', token)
                    break
                key = key_dispatch(t0, bad_dict_key)(token, next)
                token = next()
                t0 = token[1]
                if t0 not in ':=':
                    error('Expected ":" or "=" after dict key %s' % repr(key), token)
                token = next()
                t0 = token[1]
                value = value_dispatch(t0, bad_dict_value)(token, next)
                append((key, value))
                delim = next()
                t0 = delim[1]
                if t0 in ',;':
                    continue

                # Allow line ending to be used as a comma, so
                # just pretend we got a comma if on a new line
                if t0 not in '}@' and token[-2] != delim[-2]:
                    token[-1].push(delim)
                    continue
                token = delim
                break

            if t0 != '}':
                if t0 != '@':
                    error('Expected "," or "}"', token)
                if not entirestring:
                    error('Unterminated dict (no matching "}")', firsttok)

            return object_pairs_hook(result)

        key_dispatch = {'X':read_unquoted,  '"':read_quoted}.get

        value_dispatch = {'X':read_unquoted, '[':read_json_array,
                         '{': read_json_dict, '"':read_quoted}.get


        def parse(source):
            tokens = tokenizer(source, None)
            tokens.stringcache = {}.setdefault
            next = tokens.next

            firsttok = next()
            t0 = firsttok[1]
            t1 = t0 == '@' and '@' or tokens.peek()[1]
            if t0 in '{[' or t1 == '@':
                value = value_dispatch(firsttok[1], bad_top_value)(firsttok, next)
                lasttok = next()
                if lasttok[1] != '@':
                    error('Unexpected additional data', lasttok)
            else:
                tokens.push(firsttok)
                func = (t1 in ':=') and read_json_dict or read_json_array
                value = func(None, next, True)
                if tokens:
                    closing = ']}'[t1 in ':=']
                    error('Unexpected %s before this' % closing, next())
            return value


        return parse


class EJsonSystem(EJsonParser, UnquotedToken, QuotedToken, Dispatcher):
    pass

loads = EJsonSystem.dispatcher_factory()
