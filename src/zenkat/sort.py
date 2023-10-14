from zenkat.fields import get_field_fn

def sort_from_query(objs: list, sort_str : str):
    tokens = sort_str.split()
    if tokens[1] not in ('asc','desc'):
        raise ValueError()

    field = tokens[0]

    def key_fn(o):
        attr = get_field_fn(o, field)
        if isinstance(attr, str):
            attr = attr.lower()
        return attr

    return sorted(objs, key=key_fn, reverse = (tokens[1] == 'desc'))