from zenkat import zenkat, extract
from rich.console import Console

def grep(args, console: Console, config: dict):
    index = zenkat.index(args.path, config)
    regexp = args.command[1]
    data = index.pages

    filter_strs = []
    if args.filter != None:
        filter_strs = args.filter

    filters = [zenkat.parse_filter(f, data[0]) for f in filter_strs]
    filtered = zenkat.filter_objs(data, filters)

    limit_no = -1
    if args.limit != None:
        limit_no = int(args.limit)
    # context = 3
    # # how many words around the regexp to return
    # if args.context != None:
    #     context = int(args.context)
    match_no = 0

    for page in filtered:
        matches = extract.grep(page.abs_path, regexp)
        if len(matches) == 0: continue
        console.print(f"[link]{ page.abs_path }[/link]")
        for match in matches:
            console.print(f"[info]{match.line_no}[/info] {match.context}")
            match_no += 1
            if limit_no > -1 and match_no > limit_no:
                return
        console.print("")
