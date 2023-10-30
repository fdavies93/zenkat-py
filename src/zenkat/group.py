from zenkat.fields import get_field_fn
from collections import OrderedDict

def group(objects: list, field_name: str, reverse=False):
    obj_dict: OrderedDict = OrderedDict()
    for obj in objects:
        field_val = get_field_fn(obj, field_name)
        if field_val not in obj_dict: obj_dict[field_val] = []
        obj_dict[field_val].append(obj)

    ordered_dict = OrderedDict()

    for k in sorted(obj_dict.keys(), reverse=reverse):
        ordered_dict[str(k)] = obj_dict[k]
     
    return ordered_dict
