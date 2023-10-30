from zenkat import filter, sort, format, index, group
from rich.console import Console
from argparse import ArgumentParser


def make_ls_parser(parser: ArgumentParser):
    parser.add_argument(
        "corpus",
        choices=("links", "pages", "tags"),
    )
    parser.add_argument("--path", type=str, default=".")
    parser.add_argument("--quick-format", "-F")
    parser.add_argument("--format")
    parser.add_argument("--filter", "-f")
    parser.add_argument("--sort", "-s")
    parser.add_argument("--group", "-g")
    parser.add_argument("--limit", "-l")
    # maybe support recursive?


def ls(args, console: Console, config: dict):
    idx = index.index(args.path, config)

    corpus = args.corpus

    if corpus == "links":
        f_str = config["formats"]["default"]["list"]["links"]
        data = idx.links
    elif corpus == "pages":
        f_str = config["formats"]["default"]["list"]["pages"]
        data = idx.pages
    elif corpus == "tags":
        f_str = config["formats"]["default"]["list"]["tags"]
        data = idx.tags
    else:
        raise ValueError()

    quick_format = args.quick_format
    if quick_format != None:
        f_str = config["formats"][quick_format]

    if args.format != None:
        f_str = args.format

    filters = []
    if args.filter != None:
        filters = [filter.parse_filter_str(args.filter, data[0])]

    filtered = filter.filter_objs(data, filters)

    if args.sort != None:
        filtered = sort.sort_from_query(filtered, args.sort)

    if args.group != None:
        grouped = group.group(filtered, args.group)
        filtered = []
        for key, objs in grouped.items():
            filtered.extend([{"group_name": args.group,"group_value": key, "object": obj} for obj in objs]) 

    if args.limit != None:
        limit_no = int(args.limit)
        if limit_no > 0:
            filtered = filtered[:limit_no]
        elif limit_no < 0:
            filtered = filtered[limit_no:]

    ls = []
    if args.group != None:
        group_str = config["formats"]["default"]["list"]["group_line"] 
        listed: set = set()
        for joined in filtered:
            val = joined["group_value"]
            if val not in listed:
                listed.add(val)
                ln = format.format(group_str, {"group_name": args.group, "group_value": val}, console, config["theme"]["colors"])
                ls.append(ln)
            ln = format.format(f_str, joined["object"], console, config["theme"]["colors"])
            ls.append(ln)
   
    else:
        ls = [
            format.format(f_str, obj, console, config["theme"]["colors"])
        for obj in filtered
        ]

    for line in ls:
        print(line)
