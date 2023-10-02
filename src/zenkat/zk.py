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
    pages = zenkat.index(args.path, exclude)
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
    pages = get_pages(args)
    f_str = "[↓{in_link_count} ↑{out_link_count}] {title} ({rel_path})"
    if args.format != None:
        f_str = args.format
    ls = zenkat.format_list(pages, f_str)
    for line in ls: print(line)

def main():
    parser = argparse.ArgumentParser(prog="zenkat", description="Zenkat: Library and CLI to use plain markdown files as a Zettelkasten knowledge store.")
    parser.add_argument('command', choices=['list', 'tags'])
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