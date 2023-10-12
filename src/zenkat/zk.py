from zenkat import zenkat
import argparse
import sys
from pathlib import Path
from rich.console import Console
from rich.theme import Theme
from rich.markdown import Markdown
import shlex
import time
import os

def get_pages(args):
    exclude = []
    if args.exclude != None:
        exclude = args.exclude
    filter_strs = []
    if args.filter != None:
        filter_strs = args.filter
    filters = [zenkat.generate_filter(f, zenkat.Page) for f in filter_strs]
    pages = zenkat.index(args.path, exclude).pages
    filtered = zenkat.filter_objs(pages, filters)
    if args.sort != None:
        filtered = zenkat.sort_from_query(filtered, args.sort)
    return filtered

def cmd_cat(args, console: Console, config: dict):
    path = args.command[1]
    p = Path(path)
    if (p.exists() and p.suffixes[-1] == ".md"):
        document = p.read_text()
        md = Markdown(document)
        console.print(md)

def cmd_list(args, console: Console, config: dict):
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

    ls = zenkat.format_list(filtered, f_str)
    for line in ls: console.print(line)

def cmd_grep(args, console: Console, config: dict):
    index = zenkat.index(args.path, config)
    regexp = args.command[1]
    data = index.pages

    filter_strs = []
    if args.filter != None:
        filter_strs = args.filter

    filters = [zenkat.parse_filter(f, data[0]) for f in filter_strs]
    filtered = zenkat.filter_objs(data, filters)

    # context = 3
    # # how many words around the regexp to return
    # if args.context != None:
    #     context = int(args.context)

    for page in filtered:
        matches = zenkat.grep(page.abs_path, regexp)
        if len(matches) == 0: continue
        console.print(f"[link]{ page.abs_path }[/link]")
        for match in matches:
            console.print(f"[info]{match.line_no}[/info] {match.context}")
        console.print("")

def cmd_query(args, console: Console, config: dict):
    index = zenkat.index(args.path, config)
    if len(args.command) > 1 and config["queries"].get(args.command[1]) != None:
        query = config["queries"].get(args.command[1])
    elif args.query != None:
        query = args.query
    else:        
        raise ValueError("Must use the -q / --query flag when calling query or call a saved query from config.queries")
    output = zenkat.parse_query(query, index)

    corpus = output.corpus
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
    
    if output.format_str != "":
        f_str = output.format_str

    quick_format = args.quick_format
    if quick_format != None:
        f_str = config["formats"][quick_format]

    if args.format != None:
        f_str = args.format

    ls = zenkat.format_list(output.results, f_str)
    for line in ls:
        console.print(line)


def cmd_tasks(args, console: Console, config: dict):
    index = zenkat.index(args.path, config)
    # the first filter applies to the tasks
    # the second filter applies to the page
    # all others are ignored
    filter_strs = []
    if args.filter != None:
        filter_strs = args.filter

    pages = index.pages

    li_filter = None
    if len(filter_strs) > 0:
        li_filter = zenkat.parse_filter(filter_strs[0], zenkat.ListItem)
    if args.page != None:
        page_filter = zenkat.parse_filter(args.page, zenkat.Page)
        pages = list(filter(page_filter, pages))

    status_symbols = config["theme"]["tasks"]["symbols"]
    status_tags = config["theme"]["tasks"]["tags"]

    for p in pages:
        lis = []
        for ls in p.lists:
            l = ls
            if li_filter is not None: l = list(filter(li_filter, l))
            l = list(filter(lambda li: li.type == "task", l))
            lis = lis + l
        # now we have our list items filtered correctly
        if len(lis) > 0:
            console.print(f"[link]{p.title}[/link]")
        for li in lis:
            t1, t2 = "",""
            if li.status in status_tags:
                t1, t2 = status_tags[li.status]
            sym = status_symbols.get(li.status)
            console.print(f"[status]{sym}[/status] {t1}{li.text}{t2}")
            pass

def create_parser():
    parser = argparse.ArgumentParser(prog="zenkat", description="Zenkat: Library and CLI to use plain markdown files as a Zettelkasten knowledge store.")
    parser.add_argument('command', nargs="+")
    parser.add_argument('--path', nargs='?', const='.', type=str, default='.')
    parser.add_argument("-e","--exclude",action='append')
    parser.add_argument("--format")
    parser.add_argument("--quick-format","-F")
    parser.add_argument("--filter", "-f", action="append")
    parser.add_argument("--page")
    parser.add_argument("--sort", '-s')
    parser.add_argument("--query","-q")
    parser.add_argument("--recursive", "-r")
    return parser

def get_cmd_map():
    return {
        'list': cmd_list,
        'cat': cmd_cat,
        'grep': cmd_grep,
        'query': cmd_query,
        'tasks': cmd_tasks,
        'macro': cmd_macro
    }

def cmd_macro(args, console, config):
    macro_name = args.command[1]
    macro_str = config["macros"][macro_name]
    macro_arg_str = shlex.split(macro_str)
    parser = create_parser()
    cmd_map = get_cmd_map()

    macro_args = parser.parse_args(macro_arg_str)

    if args.recursive == None:
        cmd_map[macro_args.command[0]](macro_args, console, config)    
        return
    
    wait_time = float(args.recursive)
    while True:
        console.clear()
        cmd_map[macro_args.command[0]](macro_args, console, config)    
        time.sleep(wait_time)

def main():
    parser = create_parser()
    args = parser.parse_args()

    cmd_map = get_cmd_map()

    config = zenkat.load_config()
    console = Console(theme=Theme(config["theme"]["colors"]))

    cmd_map[args.command[0]](args, console, config)
    
if __name__ == "__main__":
    sys.exit(main())