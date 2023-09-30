import zenkat
import argparse

def unique_tags(pages : zenkat.Page):
    tags = set()
    for page in pages:
        tags = tags.union(page.tags)
    return tags

def filter_by_tag(pages : zenkat.Page, tag : str):
    return [p for p in pages if tag in p.tags]

def calculate_links(pages: list[zenkat.Page]):
    link_count = dict()
    for p in pages:
        for l in p.links:
            if link_count.get(l) == None:
                link_count[l] = 0
            link_count[l] += 1
    return link_count            

def cmd_list(args):
    exclude = []
    if args.exclude != None:
        exclude = args.exclude
    f_str = "{filename} ({path})"
    if args.format != None:
        f_str = args.format
    filter_strs = []
    if args.filter != None:
        filter_strs = args.filter
    filters = [zenkat.generate_filter(f) for f in filter_strs]
    pages = zenkat.index(args.path, exclude)
    filtered = zenkat.filter_pages(pages, filters)
    ls = zenkat.format_list(filtered, f_str)
    for line in ls: print(line)

def main():
    parser = argparse.ArgumentParser(prog="zk", description="Zenkat: Library and CLI to use plain markdown files as a Zettelkasten knowledge store.")
    parser.add_argument('command', choices=['list'])
    parser.add_argument('--path', nargs='?', const='.', type=str, default='.')
    parser.add_argument("-e","--exclude",action='append')
    parser.add_argument("--format", "-F")
    parser.add_argument("--filter", "-f", action="append")
    args = parser.parse_args()
    
    if args.command == 'list':
        cmd_list(args)
    
if __name__ == "__main__":
    main()