'''
Parser for RSON

Copyright (c) 2010, Patrick Maupin.  All rights reserved.

See http://code.google.com/p/rson/source/browse/#svn/trunk/license.txt

'''

class RsonParser(object):
    ''' Parser for RSON
    '''

    allow_trailing_commas = True

    def parser_factory(self, len=len, type=type, isinstance=isinstance, list=list):

        Tokenizer = self.Tokenizer
        tokenizer = Tokenizer.factory()
        error = Tokenizer.error

        read_unquoted = self.unquoted_parse_factory()
        read_quoted = self.quoted_parse_factory()
        parse_equals = self.equal_parse_factory(read_unquoted)
        new_object, new_array = self.object_type_factory()
        allow_trailing_commas = self.allow_trailing_commas
        disallow_missing_object_keys = self.disallow_missing_object_keys
        key_handling = [disallow_missing_object_keys, self.disallow_multiple_object_keys]


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
            result = new_array()
            append = result.append
            while 1:
                token = next()
                t0 = token[1]
                if t0 == ']':
                    if result and not allow_trailing_commas:
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

        def read_json_dict(token, next):
            result = []
            append = result.append
            while 1:
                token = next()
                t0 = token[1]
                if t0  == '}':
                    if result and not allow_trailing_commas:
                        error('Unexpected trailing comma', token)
                    break
                key = json_value_dispatch(t0, bad_dict_key)(token, next)
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
            return new_object(result)

        json_value_dispatch = {'X':read_unquoted, '[':read_json_array,
                               '{': read_json_dict, '"':read_quoted}.get


        rson_value_dispatch = {'X':read_unquoted, '[':read_json_array,
                                  '{': read_json_dict, '"':read_quoted,
                                   '=': parse_equals}.get


        empty_object = new_object([])
        empty_array = new_array()
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
                            result[-1], token = parse_recurse_dict(stack, next, token, [])
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

        def parse_one_dict_entry(stack, next, token, entry):
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
            return entry, token

        def parse_recurse_dict(stack, next, token, result):
            arrayindent = stack[-1][4]
            while 1:
                thisindent = token[4]
                if thisindent != arrayindent:
                    if thisindent < arrayindent:
                        return new_object(result), token
                    bad_unindent(token, next)
                key = json_value_dispatch(token[1], bad_top_value)(token, next)
                stack[-1] = token
                entry, token = parse_one_dict_entry(stack, next, next(), [key])
                result.append(entry)

        def parse_recurse(stack, next):
            ''' parse_recurse ALWAYS returns a list or a dict.
                (or the user variants thereof)
                It is up to the caller to determine that it was an array
                of length 1 and strip the contents out of the array.
            '''
            firsttok = stack[-1]
            if firsttok[1] == '=':
                return parse_recurse_array(stack, next, firsttok, new_array())

            value = json_value_dispatch(firsttok[1], bad_top_value)(firsttok, next)
            token = next()

            # We return an array if the next value is on a new line and either
            # is at the same indentation, or the current value is an empty list

            if (token[5] != firsttok[5] and
                    (token[4] <= firsttok[4] or
                     value == empty_array) and disallow_missing_object_keys):
                return parse_recurse_array(stack, next, token, new_array([value]))

            # Otherwise, return a dict
            entry, token = parse_one_dict_entry(stack, next, token, [value])
            return parse_recurse_dict(stack, next, token, [entry])


        def parse(source):
            tokens = tokenizer(source, None)
            tokens.stringcache = {}.setdefault
            next = tokens.next
            value, token = parse_recurse([next()], next)
            if token[1] != '@':
                error('Unexpected additional data', token)
            if len(value) == 1 and isinstance(value, list):
                value = value[0]
            return value

        return parse
