from zenkat import zenkat
import argparse
import sys
from pathlib import Path
from rich.console import Console
from rich.theme import Theme
from rich.markdown import Markdown

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
    index = zenkat.index(args.path)
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
    index = zenkat.index(args.path)
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
    index = zenkat.index(args.path)
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

def main():
    parser = argparse.ArgumentParser(prog="zenkat", description="Zenkat: Library and CLI to use plain markdown files as a Zettelkasten knowledge store.")
    parser.add_argument('command', nargs="+")
    parser.add_argument('--path', nargs='?', const='.', type=str, default='.')
    parser.add_argument("-e","--exclude",action='append')
    parser.add_argument("--format")
    parser.add_argument("--quick-format","-F")
    parser.add_argument("--filter", "-f", action="append")
    parser.add_argument("--sort", '-s')
    parser.add_argument("--query","-q")
    args = parser.parse_args()

    cmd_map = {
        'list': cmd_list,
        'cat': cmd_cat,
        'grep': cmd_grep,
        'query': cmd_query
    }

    config = zenkat.load_config()
    console = Console(theme=Theme(config["theme"]["colors"]))

    cmd_map[args.command[0]](args, console, config)
    
if __name__ == "__main__":
    sys.exit(main())