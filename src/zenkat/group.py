from zenkat.fields import get_field_fn
from collections import OrderedDict
from dataclasses import dataclass
import typing

@dataclass
class GroupedListItem():
    group_name: str
    group_value: str
    obj: object


def group(objects: list, field_name: str, reverse=False):
    obj_dict: OrderedDict = OrderedDict()
    for obj in objects:
        field_val = get_field_fn(obj, field_name)
        if not isinstance(field_val, typing.Hashable):
            field_val = str(field_val)
        if field_val not in obj_dict: obj_dict[field_val] = []
        obj_dict[field_val].append(obj)

    # ensure that group fields are sorted
    ordered_dict = OrderedDict()

    for k in sorted(obj_dict.keys(), reverse=reverse):
        ordered_dict[str(k)] = obj_dict[k]
     
    return ordered_dict

def flatten(group_name: str, grouped: OrderedDict) -> list[dict]:
    flattened: list = []
    for key, objs in grouped.items():
        flattened.extend([GroupedListItem(group_name, key, obj) for obj in objs])
    return flattened
