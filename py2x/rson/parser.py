'''
Parser for RSON

Copyright (c) 2010, Patrick Maupin.  All rights reserved.

See http://code.google.com/p/rson/source/browse/#svn/trunk/license.txt

'''

class RsonParser(object):
    ''' Parser for RSON
    '''

    object_hook = None
    object_pairs_hook = None
    allow_trailing_commas = True
    use_decimal = False
    array_hook = list

    def parser_factory(self):

        Tokenizer = self.Tokenizer
        tokenizer = Tokenizer.factory()
        error = Tokenizer.error

        if self.use_decimal:
            from decimal import Decimal
            self.parse_float = Decimal

        read_unquoted = self.unquoted_parse_factory()
        read_quoted = self.quoted_parse_factory()
        allow_trailing_commas = self.allow_trailing_commas

        object_hook = self.object_hook
        object_pairs_hook = self.object_pairs_hook
        if object_pairs_hook is None:
            if object_hook is None:
                object_pairs_hook = self.dict_factory()
            else:
                mydict = dict
                object_pairs_hook = lambda x: object_hook(mydict(x))

        array_hook = self.array_hook

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
            result = array_hook()
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
                key = json_key_dispatch(t0, bad_dict_key)(token, next)
                token = next()
                t0 = token[1]
                if t0 != ':':
                    error('Expected ":" after dict key %s' % repr(key), token)
                token = next()
                t0 = token[1]
                value = json_value_dispatch(t0, bad_dict_value)(token, next)
                append((key, value))
                delim = next()
                t0 = delim[1]
                if t0 == ',':
                    continue
                if t0 != '}':
                    if t0 == '@':
                        error('Unterminated dict (no matching "}")', firsttok)
                    error('Expected "," or "}"', delim)
                break
            return object_pairs_hook(result)

        def parse_equals(token, next):
            error('Equals processing not implemented yet', token)

        json_key_dispatch = {'X':read_unquoted,  '"':read_quoted}.get

        json_value_dispatch = {'X':read_unquoted, '[':read_json_array,
                               '{': read_json_dict, '"':read_quoted}.get


        rson_value_dispatch = {'X':read_unquoted, '[':read_json_array,
                                  '{': read_json_dict, '"':read_quoted,
                                   '=': parse_equals}.get


        empty_object = object_pairs_hook([])
        empty_array = array_hook()
        empties = empty_object, empty_array

        def parse_recurse_array(stack, next, token, result):
            arrayindent, linenum = stack[-1][4:6]
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
                    if type(entry[-1]) == type(value):
                        entry[-1] = value
                    else:
                        error('Cannot load %s into %s' % (type(value), type(entry[-1])), stack[-1])
                else:
                    entry.append(value)
                stack.pop()
            elif len(entry) < 2:
                error('Expected ":" or "=", or indented line', token)
            return entry, token

        def parse_recurse_dict(stack, next, token, result):
            arrayindent = stack[-1][4]
            while 1:
                thisindent = token[4]
                if thisindent != arrayindent:
                    if thisindent < arrayindent:
                        return object_pairs_hook(result), token
                    bad_unindent(token, next)
                key = json_value_dispatch(token[1], bad_top_value)(token, next)
                stack[-1] = token
                entry, token = parse_one_dict_entry(stack, next, next(), [key])
                result.append(entry)

        def parse_recurse(stack, next):
            firsttok = stack[-1]
            if firsttok[1] == '=':
                value, token = parse_recurse_array(stack, next, firsttok, array_hook())
                if len(value) == 1:
                    value = value[0]
                return value, token

            value = json_value_dispatch(firsttok[1], bad_top_value)(firsttok, next)
            token = next()
            ttype = token[1]
            if ttype not in ':=@':
                return parse_recurse_array(stack, next, token, array_hook([value]))
            if ttype == '@':
                return value, token

            entry, token = parse_one_dict_entry(stack, next, token, [value])
            return parse_recurse_dict(stack, next, token, [entry])


        def parse(source):
            tokens = tokenizer(source, None)
            tokens.stringcache = {}.setdefault
            next = tokens.next
            value, token = parse_recurse([next()], next)
            if token[1] != '@':
                error('Unexpected additional data', token)
            return value

        return parse
