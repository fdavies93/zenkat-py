from zenkat.fields import get_field_fn, convert_to_type
from typing import Callable, Tuple

def get_operator(op_str):
    operator_map = {
        '=': lambda a, b : a == b,
        '~': lambda a, b : a != b,
        'has': lambda a, b : b in a,
        '~has': lambda a, b : b not in a,
        '>': lambda a, b : a > b,
        '<': lambda a, b : a < b,
        '>=': lambda a, b : a >= b,
        '<=': lambda a, b : a <= b
    }
    return operator_map[op_str]

def lex_filter_str(filter_str: str) -> list[str]:
    cur_token = ''
    tokens = []
    # because tokens and strings have a 1:1 correspondence in this case we don't need a separate dataclass
    
    # lexing step - technically a state machine but so simple it doesn't need to maintain formal state
    for char in filter_str:
        if char == ' ':
            if len(cur_token) > 0: 
                tokens.append(cur_token)
                cur_token = ''
            continue
        if char in ('(',')'):
            to_add = []
            if len(cur_token) > 0: to_add.append(cur_token)
            to_add.append(char)
            tokens.extend(to_add)
            cur_token = ''
            continue
        cur_token += char
    if len(cur_token) > 0: tokens.append(cur_token)
    return tokens

# returns tuple which is left (parsed) and right (remaining)
def parse_filter_expr(tokens: list[str]) -> Tuple[list,list]:
    # extends parse_filter to work on compound filter_objs by supporting nested brackets and AND / OR statements
    # grouping (AST) step

    remaining = tokens
    out = []
    
    if remaining[0] == '(':
        result = parse_filter_expr(tokens[1:])
        out = result[0]
        remaining = result[1]

    if len(remaining) == 0:
        return (out, remaining)

    finish_early = False
    for i, token in enumerate(remaining[:4]):
        if token in (')', 'and', 'or'):
            if i != 3: raise ValueError()
            finish_early = True
            out.append(' '.join(remaining[:3]))
            remaining = remaining[3:]
    
    if not finish_early:
        out.append(' '.join(remaining[:4]))
        remaining = remaining[4:]

    if len(remaining) > 0 and remaining[0] == ')':
        return (out, remaining)

    if len(remaining) > 0 and remaining[0] in ('and','or'):
        result = parse_filter_expr(remaining[1:])
        return ([out,remaining[0],result[0]], result[1])
    return (out, remaining)


def parse_filter_str(filter_str: str, data_type):    
    tokens = lex_filter_str(filter_str)
    return parse_filter_expr(tokens)

def parse_filter(filter_str: str, data_type):
    # this syntax is good for a /single/ instance of a filter but won't work for compound filters
        
    tokens = filter_str.split() # 'lexing' the filter
    
    set_transform = None
    if tokens[0] in ("any","all"):
        set_transform = tokens[0]
        tokens = tokens[1:]

    # get fields from object
    field_specifier = tokens[0]

    operation = get_operator(tokens[1])

    tokens[2] = " ".join(tokens[2:])

    def filter_fn(o):
        # get field values
        field = get_field_fn(o, field_specifier)
        # convert comparator to correct type based on field
        comparator = convert_to_type(tokens[2], type(field))
        # get operation
        my_op = operation
        
        if set_transform is not None:
            truth_vals = [my_op(f,comparator) for f in field]
            if len(truth_vals) == 0: return False
            if set_transform == "any": result = any(truth_vals)
            elif set_transform == "all": result = all(truth_vals)
            return result

        result = my_op(field, comparator)
        return result

    return filter_fn

def filter_objs(objs: list, filters: list[Callable]):
    out = objs
    for f in filters:
        out = list(filter(f, out))
    return out
