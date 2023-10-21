from zenkat import index, extract, filter, objects
from rich.console import Console
from dataclasses import dataclass
from argparse import ArgumentParser

def make_grep_parser(parser: ArgumentParser):
    parser.add_argument("pattern")
    parser.add_argument('--path', type=str, default='.')
    parser.add_argument("--filter","-f")
    parser.add_argument("--limit", "-l")
    # AWESOME scope for adding different types of pattern match flags (case-sensitive, exact match, etc here)

def grep(args, console: Console, config: dict):
    idx = index.index(args.path, config)
    regexp = args.pattern
    data = idx.pages

    filters = []
    if args.filter != None:
        filter_str = args.filter
        filters = [filter.parse_filter_str(filter_str, objects.Page)]
    
    filtered = filter.filter_objs(data, filters)

    limit_no = -1
    if args.limit != None:
        limit_no = int(args.limit)
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
