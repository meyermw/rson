'''
Parser for RSON

Copyright (c) 2010, Patrick Maupin.  All rights reserved.

See http://code.google.com/p/rson/source/browse/trunk/license.txt
'''

from rson.py23 import basestring

class RsonParser(object):
    ''' Parser for RSON
    '''

    disallow_trailing_commas = True
    disallow_rson_sublists = False
    disallow_rson_subdicts = False

    @staticmethod
    def post_parse(tokens, value):
        return value

    def client_info(self, parse_locals):
        pass

    def parser_factory(self, len=len, type=type, isinstance=isinstance, list=list, basestring=basestring):

        Tokenizer = self.Tokenizer
        tokenizer = Tokenizer.factory()
        error = Tokenizer.error

        read_unquoted = self.unquoted_parse_factory()
        read_quoted = self.quoted_parse_factory()
        parse_equals = self.equal_parse_factory(read_unquoted)
        new_object, new_array = self.object_type_factory()
        disallow_trailing_commas = self.disallow_trailing_commas
        disallow_missing_object_keys = self.disallow_missing_object_keys
        key_handling = [disallow_missing_object_keys, self.disallow_multiple_object_keys]
        disallow_nonstring_keys = self.disallow_nonstring_keys
        post_parse = self.post_parse


        def bad_array_element(token, next):
            error('Expected array element', token)

        def bad_dict_key(token, next):
            error('Expected dictionary key', token)

        def bad_dict_value(token, next):
            error('Expected dictionary value', token)

        def bad_top_value(token, next):
            error('Expected start of object', token)

        def bad_unindent(token, next):
            error('Unindent does not match any outer indentation level', token)

        def bad_indent(token, next):
            error('Unexpected indentation', token)

        def read_json_array(firsttok, next):
            result = new_array([], firsttok)
            append = result.append
            while 1:
                token = next()
                t0 = token[1]
                if t0 == ']':
                    if result and disallow_trailing_commas:
                        error('Unexpected trailing comma', token)
                    break
                append(json_value_dispatch(t0,  bad_array_element)(token, next))
                delim = next()
                t0 = delim[1]
                if t0 == ',':
                    continue
                if t0 != ']':
                    if t0 == '@':
                        error('Unterminated list (no matching "]")', firsttok)
                    error('Expected "," or "]"', delim)
                break
            return result

        def read_json_dict(firsttok, next):
            result = new_object()
            append = result.append
            while 1:
                token = next()
                t0 = token[1]
                if t0  == '}':
                    if result and disallow_trailing_commas:
                        error('Unexpected trailing comma', token)
                    break
                key = json_value_dispatch(t0, bad_dict_key)(token, next)
                if disallow_nonstring_keys and not isinstance(key, basestring):
                    error('Non-string key %s not supported' % repr(key), token)
                token = next()
                t0 = token[1]
                if t0 != ':':
                    error('Expected ":" after dict key %s' % repr(key), token)
                token = next()
                t0 = token[1]
                value = json_value_dispatch(t0, bad_dict_value)(token, next)
                append([key, value])
                delim = next()
                t0 = delim[1]
                if t0 == ',':
                    continue
                if t0 != '}':
                    if t0 == '@':
                        error('Unterminated dict (no matching "}")', firsttok)
                    error('Expected "," or "}"', delim)
                break
            return result.get_result(firsttok)

        def read_rson_unquoted(firsttok, next):
            toklist = []
            linenum = firsttok[5]
            while 1:
                token = next()
                if token[5] != linenum or token[1] in ':=':
                    break
                toklist.append(token)
            firsttok[-1].push(token)
            if not toklist:
                return read_unquoted(firsttok, next)
            s = list(firsttok[2:4])
            for tok in toklist:
                s.extend(tok[2:4])
            result = list(firsttok)
            result[3] = s.pop()
            result[2] = ''.join(s)
            return read_unquoted(result, next)

        json_value_dispatch = {'X':read_unquoted, '[':read_json_array,
                               '{': read_json_dict, '"':read_quoted}.get


        rson_value_dispatch = {'X':read_rson_unquoted, '[':read_json_array,
                                  '{': read_json_dict, '"':read_quoted,
                                   '=': parse_equals}

        if self.disallow_rson_sublists:
            rson_value_dispatch['['] = read_rson_unquoted

        if self.disallow_rson_subdicts:
            rson_value_dispatch['{'] = read_rson_unquoted

        rson_key_dispatch = rson_value_dispatch.copy()
        if disallow_missing_object_keys:
            del rson_key_dispatch['=']

        rson_value_dispatch = rson_value_dispatch.get
        rson_key_dispatch = rson_key_dispatch.get

        empty_object = new_object().get_result(None)
        empty_array = new_array([], None)
        empty_array_type = type(empty_array)
        empties = empty_object, empty_array

        def parse_recurse_array(stack, next, token, result):
            arrayindent, linenum = stack[-1][4:6]
            linenum -= not result
            while 1:
                thisindent, newlinenum = token[4:6]
                if thisindent != arrayindent:
                    if thisindent < arrayindent:
                        return result, token
                    if result:
                        stack.append(token)
                        lastitem = result[-1]
                        if lastitem == empty_array:
                            result[-1], token = parse_recurse_array(stack, next, token, lastitem)
                        elif lastitem == empty_object:
                            result[-1], token = parse_recurse_dict(stack, next, token, lastitem)
                        else:
                            result = None
                    if result:
                        stack.pop()
                        thisindent, newlinenum = token[4:6]
                        if thisindent <= arrayindent:
                            continue
                        bad_unindent(token, next)
                    bad_indent(token, next)
                if newlinenum <= linenum:
                    if token[1] in '=:':
                        error('Cannot mix list elements with dict (key/value) elements', token)
                    error('Array elements must either be on separate lines or enclosed in []', token)
                linenum = newlinenum
                value = rson_value_dispatch(token[1], bad_top_value)(token, next)
                result.append(value)
                token = next()

        def parse_one_dict_entry(stack, next, token, entry, mydict):
            arrayindent, linenum = stack[-1][4:6]
            while token[1] == ':':
                tok1 = next()
                thisindent, newlinenum = tok1[4:6]
                if newlinenum == linenum:
                    value = rson_value_dispatch(tok1[1], bad_top_value)(tok1, next)
                    token = next()
                    entry.append(value)
                    continue
                if thisindent <= arrayindent:
                    error('Expected indented line after ":"', token)
                token = tok1

            if not entry:
                error('Expected key', token)

            thisindent, newlinenum = token[4:6]
            if newlinenum == linenum and token[1] == '=':
                value = rson_value_dispatch(token[1], bad_top_value)(token, next)
                entry.append(value)
                token = next()
            elif thisindent > arrayindent:
                stack.append(token)
                value, token = parse_recurse(stack, next)
                if entry[-1] in empties:
                    if type(entry[-1]) is type(value):
                        entry[-1] = value
                    else:
                        error('Cannot load %s into %s' % (type(value), type(entry[-1])), stack[-1])
                elif len(value) == 1 and type(value) is empty_array_type:
                    entry.extend(value)
                else:
                    entry.append(value)
                stack.pop()
            length = len(entry)
            if length != 2  and key_handling[length > 2]:
                if length < 2:
                    error('Expected ":" or "=", or indented line', token)
                error("rson client's object handlers do not support chained objects", token)
            if disallow_nonstring_keys:
                for key in entry[:-1]:
                    if not isinstance(key, basestring):
                        error('Non-string key %s not supported' % repr(key), token)
            mydict.append(entry)
            return token

        def parse_recurse_dict(stack, next, token, result):
            arrayindent = stack[-1][4]
            while 1:
                thisindent = token[4]
                if thisindent != arrayindent:
                    if thisindent < arrayindent:
                        return result.get_result(token), token
                    bad_unindent(token, next)
                key = rson_key_dispatch(token[1], bad_top_value)(token, next)
                stack[-1] = token
                token = parse_one_dict_entry(stack, next, next(), [key], result)

        def parse_recurse(stack, next, tokens=None):
            ''' parse_recurse ALWAYS returns a list or a dict.
                (or the user variants thereof)
                It is up to the caller to determine that it was an array
                of length 1 and strip the contents out of the array.
            '''
            firsttok = stack[-1]
            value = rson_value_dispatch(firsttok[1], bad_top_value)(firsttok, next)

            # We return an array if the next value is on a new line and either
            # is at the same indentation, or the current value is an empty list

            token = next()
            if (token[5] != firsttok[5] and
                    (token[4] <= firsttok[4] or
                     value in empties) and disallow_missing_object_keys):
                result = new_array([value], firsttok)
                if tokens is not None:
                    tokens.top_object = result
                return parse_recurse_array(stack, next, token, result)

            # Otherwise, return a dict
            result = new_object()
            if tokens is not None:
                tokens.top_object = result
            token = parse_one_dict_entry(stack, next, token, [value], result)
            return parse_recurse_dict(stack, next, token, result)


        def parse(source):
            tokens = tokenizer(source, None)
            tokens.stringcache = {}.setdefault
            tokens.client_info = client_info
            next = tokens.next
            value, token = parse_recurse([next()], next, tokens)
            if token[1] != '@':
                error('Unexpected additional data', token)

            # If it's a single item and we don't have a specialized
            # object builder, just strip the outer list.
            if (len(value) == 1 and isinstance(value, list)
                   and disallow_missing_object_keys):
                value = value[0]
            return post_parse(tokens, value)

        client_info = self.client_info(locals())

        return parse
