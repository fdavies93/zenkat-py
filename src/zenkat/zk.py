from zenkat import zenkat
import argparse
import sys
from rich.console import Console
from rich.theme import Theme

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

def cmd_list(args, console):
    index = zenkat.index(args.path)

    if args.corpus == "links":
        f_str = "[link]{doc_abs_path}[/link] → [link]{href_resolved}[/link]"
        data = index.links
    elif args.corpus == "pages": 
        f_str = "[info][↓{in_link_count} ↑{out_link_count}][/info] [main]{title}[/main], [sub]{word_count} words ([link]{rel_path}[/link])[/sub]"
        data = index.pages
    elif args.corpus == "tags": 
        f_str = "[info][{count} pages][/info] [main]{name}[/main]"
        data = index.tags
    else: raise ValueError()
    
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

def main():
    parser = argparse.ArgumentParser(prog="zenkat", description="Zenkat: Library and CLI to use plain markdown files as a Zettelkasten knowledge store.")
    parser.add_argument('command', choices=['list'])
    parser.add_argument('corpus', choices=['links','pages','tags'])
    parser.add_argument('--path', nargs='?', const='.', type=str, default='.')
    parser.add_argument("-e","--exclude",action='append')
    parser.add_argument("--format", "-F")
    parser.add_argument("--filter", "-f", action="append")
    parser.add_argument("--sort", '-s')
    args = parser.parse_args()

    cmd_map = {
        'list': cmd_list
    }

    config = zenkat.load_config()
    console = Console(theme=Theme(config["theme"]["colors"], inherit=False))

    cmd_map[args.command](args, console)
    
if __name__ == "__main__":
    sys.exit(main())