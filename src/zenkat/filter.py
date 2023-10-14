from zenkat.fields import get_field_fn, convert_to_type
from typing import Callable

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

def parse_filter(filter_str: str, data_type):
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
