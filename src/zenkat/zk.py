from zenkat import zenkat
import argparse
import sys

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

def cmd_tags(args):
    pages = get_pages(args)
    tags = set()
    for page in pages:
        tags = tags.union(page.tags)
    for tag in tags: print(tag)

def cmd_list(args):
    index = zenkat.index(args.path)

    if args.corpus == "links":
        f_str = "{doc_abs_path} → {href_resolved}"
        data = index.links
    elif args.corpus == "pages": 
        f_str = "[↓{in_link_count} ↑{out_link_count}] {title}, {word_count} words ({rel_path})"
        data = index.pages
    elif args.corpus == "tags": 
        f_str = "[{count} pages] {name}"
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
    for line in ls: print(line)

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
        'list': cmd_list,
        'tags': cmd_tags
    }

    cmd_map[args.command](args)
    
if __name__ == "__main__":
    sys.exit(main())