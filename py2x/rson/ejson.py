'''
"enhanced" JSON syntax -- no indentation support, but a few other RSON features.

Copyright (c) 2010, Patrick Maupin.  All rights reserved.

See http://code.google.com/p/rson/source/browse/#svn/trunk/license.txt
'''

from rson.tokenizer import Tokenizer
from rson.unquoted import UnquotedToken
from rson.doublequoted import QuotedToken


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
    UnquotedToken = UnquotedToken
    QuotedToken = QuotedToken

    object_hooks = None, None

    def error(self, s, token):
        if token[1] == '@':
            loc = 'at end of string'
        else:
            text = token[2]
            linenum = token[5]
            offset = -token[0]
            if linenum != 1:
                offset -= self.tokens.source.rfind('\n', offset)
            loc = 'line %s, column %s, text %s' % (linenum, offset, repr(text[:20]))
        raise ValueError('%s: %s' % (s, loc))

    @classmethod
    def factory(cls):

        tokenizer = cls.Tokenizer.factory()
        read_unquoted = cls.UnquotedToken.factory()
        read_quoted = cls.QuotedToken.factory()
        all_delimiters = cls.Tokenizer.delimiterset
        object_hook, object_pairs_hook = cls.object_hooks


        def parse(source):

            def bad_array_element(token):
                self.error('Expected array element', token)

            def bad_dict_key(token):
                self.error('Expected dictionary key', token)

            def bad_dict_value(token):
                self.error('Expected dictionary value', token)

            def bad_top_value(token):
                self.error('Expected start of object', token)

            def read_json_array(token):
                result = []
                append = result.append
                while 1:
                    token = next()
                    t0 = token[1]
                    if t0 == ']':
                        return result
                    append(json_dispatch(t0,  bad_array_element)(token))
                    token = next()
                    t0 = token[1]
                    if t0 ==',':
                        continue
                    if t0 == ']':
                        return result
                    self.error('Expected ]', token)

            def read_json_dict(token):
                result = {}
                while 1:
                    token = next()
                    t0 = token[1]
                    if t0  == '}':
                        return result
                    key = key_dispatch(t0, bad_dict_key)(token)
                    token = next()
                    t0 = token[1]
                    if t0 not in ':=':
                        self.error('Expected : or = after dict key', token)
                    token = next()
                    t0 = token[1]
                    value = json_dispatch(t0, bad_dict_value)(token)
                    result[key] = value
                    token = next()
                    t0 = token[1]
                    if t0 == ',':
                        continue
                    if t0 != '}':
                        self.error('Expected , or }', token)
                    if object_pairs_hook is not None:
                        return map(object_pairs_hook, result.iteritems())
                    if object_hook is not None:
                        result = object_hook(result)
                    return result

            key_dispatch = {'X':read_unquoted,  '"':read_quoted}.get

            json_dispatch = {'X':read_unquoted, '[':read_json_array,
                             '{': read_json_dict, '"':read_quoted}.get

            self = cls()
            self.tokens = tokens = tokenizer(source, self)
            next = tokens.next
            peek = tokens.peek
            push = tokens.push
            lookahead = tokens.lookahead

            firsttok = next()
            value = json_dispatch(firsttok[1], bad_top_value)(firsttok)
            lasttok = next()
            if lasttok[1] != '@':
                self.error('Expected end of string', token)
            return value

        return parse


loads = EJsonParser.factory()
