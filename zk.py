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

argparse.ArgumentParser(prog="Zenkat", description="Library and CLI to use plain markdown files as a Zettelkasten knowledge store.")

def main():
    pages = zenkat.index(".", exclude=[".excalidraw"])
    print(unique_tags(pages))
    print(calculate_links(pages))
    # print(filter_by_tag(pages, "#ffffff"))
    
if __name__ == "__main__":
    main()