from zenkat import zenkat
from rich.console import Console

def ls(args, console: Console, config: dict):
    index = zenkat.index(args.path, config)
    corpus = args.command[1]

    if corpus == "links":
        f_str = config["formats"]["default"]["list"]["links"]
        data = index.links
    elif corpus == "pages": 
        f_str = config["formats"]["default"]["list"]["pages"]
        data = index.pages
    elif corpus == "tags": 
        f_str = config["formats"]["default"]["list"]["tags"]
        data = index.tags
    elif corpus == "list_items":
        f_str = config["formats"]["default"]["list"]["list_items"]
        data = index.list_items
    else: raise ValueError()

    quick_format = args.quick_format
    if quick_format != None:
        f_str = config["formats"][quick_format]
    
    if args.format != None:
        f_str = args.format

    filter_strs = []
    if args.filter != None:
        filter_strs = args.filter

    filters = [zenkat.parse_filter(f, data[0]) for f in filter_strs]

    filtered = zenkat.filter_objs(data, filters)
    
    if args.sort != None:
        filtered = zenkat.sort_from_query(filtered, args.sort)

    if args.limit != None:
        limit_no = int(args.limit)
        if limit_no > 0:
            filtered = filtered[:limit_no]
        elif limit_no < 0:
            filtered = filtered[limit_no:]

    ls = zenkat.format_list(filtered, f_str)
    for line in ls: console.print(line)
