import dateutil
from datetime import datetime

def convert_date_str(date_str : str):
    return dateutil.parser.parse(date_str)

def get_field_simple(obj, field: str):
    if type(obj) == list:
        obj_dict = { str(i): el for i, el in enumerate(obj) }
    elif type(obj) == dict:
        obj_dict = obj
    else:
        # it's probably a dataclass
        obj_dict = obj.__dict__

    return obj_dict.get(field)

def get_field_fn(root, field_name: str):
    parts = field_name.split(".")
    obj = root
    for i, part in enumerate(parts):
        # * for reduce
        field = get_field_simple(obj, part)
        
        if field == None and type(obj) == list:
            if part == "*":
                field = reduce(lambda acc, o: acc + o, obj, [])
            else:                
                field = list(map(lambda o : get_field_simple(o, part), obj))
        obj = field
    return obj

def convert_to_type(input_str, type_info):
    if type_info == datetime:
        output = convert_date_str(input_str)
    elif type_info == int:
        output = int(input_str)
    elif type_info == str:
        output = input_str
    else:
        output = input_str # sets could potentially use a lisp        
    return output

