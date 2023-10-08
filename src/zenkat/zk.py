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

def cmd_cat(args, console: Console):
    path = args.command[1]
    p = Path(path)
    if (p.exists() and p.suffixes[-1] == ".md"):
        document = p.read_text()
        md = Markdown(document)
        console.print(md)

def cmd_list(args, console):
    index = zenkat.index(args.path)
    corpus = args.command[1]

    if corpus == "links":
        f_str = "[link]{doc_abs_path}[/link] → [link]{href_resolved}[/link]"
        data = index.links
    elif corpus == "pages": 
        f_str = "[info][↓{in_link_count} ↑{out_link_count}][/info] [main]{title}[/main], [sub]{word_count} words ([link]{rel_path}[/link])[/sub]"
        data = index.pages
    elif corpus == "tags": 
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
    parser.add_argument('command', nargs="+")
    parser.add_argument('--path', nargs='?', const='.', type=str, default='.')
    parser.add_argument("-e","--exclude",action='append')
    parser.add_argument("--format", "-F")
    parser.add_argument("--filter", "-f", action="append")
    parser.add_argument("--sort", '-s')
    args = parser.parse_args()

    cmd_map = {
        'list': cmd_list,
        'cat': cmd_cat
    }

    config = zenkat.load_config()
    console = Console(theme=Theme(config["theme"]["colors"]))

    cmd_map[args.command[0]](args, console)
    
if __name__ == "__main__":
    sys.exit(main())