from zenkat.fields import get_field_fn

def group(objects: list, field_name: str):
    obj_dict = dict()
    for obj in objects:
        field_val = str(get_field_fn(obj, field_name))
        if field_val not in obj_dict: obj_dict[field_val] = []
        obj_dict[field_val].append(obj)
     
    return obj_dict
