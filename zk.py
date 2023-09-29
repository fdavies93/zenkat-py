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
    pages = zenkat.index(args.path, exclude)
    for p in pages:
        print(f"{p.filename} ({p.path})")

def main():
    parser = argparse.ArgumentParser(prog="zk", description="Zenkat: Library and CLI to use plain markdown files as a Zettelkasten knowledge store.")
    parser.add_argument('command', choices=['list'])
    parser.add_argument('--path', nargs='?', const='.', type=str, default='.')
    parser.add_argument("-e","--exclude",action='append')
    args = parser.parse_args()
    
    if args.command == 'list':
        cmd_list(args)
    
if __name__ == "__main__":
    main()