from argparse import ArgumentParser
from dataclasses import dataclass, field, asdict
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Callable
import re
from functools import cmp_to_key
from operator import attrgetter

@dataclass()
class Page:
    title: str
    filename: str
    abs_path: str
    rel_path: str
    created_at: datetime
    modified_at: datetime
    tags: set[str] = field(default_factory=set)
    out_links: set[str] = field(default_factory=set)
    out_link_count: int = 0
    in_links: set[str] = field(default_factory=set)
    in_link_count: int = 0
    
def get_tags(document: str):
    matches = re.findall("(?:^|\s)#([-_\w\d]+)",document)
    return set(matches)

def get_wiki_links(document : str):
    matches = re.findall("(?:^|\s)\[\[([#\/\-\w\s]+)\]\]", document)
    # might want to resolve to an absolute path
    return set(matches)
    
def index(path : str, exclude : list = []):
    pages = []
    for p in Path(path).rglob("*.md"):
        suffixes = set(p.suffixes)
        if len(suffixes.intersection(exclude)) > 0:
            continue
        
        abs = str(p.absolute())

        title = p
        while title.suffix: title = title.with_suffix("")
        title = title.name
        
        cur_page = Page(
            title,
            p.name,
            abs,
            str(p.relative_to(path)),
            datetime.fromtimestamp(os.path.getctime(abs)),
            datetime.fromtimestamp(os.path.getmtime(abs))
        )
        document = p.read_text()
        cur_page.tags = get_tags(document)
        cur_page.out_links = get_wiki_links(document)
        cur_page.out_link_count = len(cur_page.out_links)
        
        pages.append(cur_page)
    return pages

def get_content(page : Page):
    with open(page.abs_path, 'r') as f:
        content = f.read()
    return content

def format_list(pages : list[Page], f_str : str):
    outputs = []
    for p in pages:
        o = asdict(p)
        outputs.append(f_str.format_map(o))
    return outputs

def generate_filter(filter_str : str, date_format = "%b %d %Y %I:%M%p"):
    tokens = filter_str.split()
    tokens[2] = ' '.join(tokens[2:])

    operator_map = {
        '=': lambda a, b : a == b,
        'has': lambda a, b : b in a,
        '>': lambda a, b : a > b,
        '<': lambda a, b : a < b,
        '>=': lambda a, b : a >= b,
        '<=': lambda a, b : a <= b
    }
    fn = operator_map[tokens[1]]

    if tokens[0] in ("created_at", "modified_at"):
        tokens[2] = datetime.strptime(tokens[2],date_format)
    elif tokens[0] in ("out_link_count", "in_link_count"):
        tokens[2] = int(tokens[2])

    return lambda p : fn(p.__dict__[tokens[0]], tokens[2])

def filter_pages(pages : list[Page], filters: list[Callable]):
    out = pages
    for f in filters:
        out = list(filter(f, out))
    return out
    
def sort_from_query(pages: list[Page], sort_str : str):
    tokens = sort_str.split()
    if tokens[1] not in ('asc','desc'):
        raise ValueError()

    field = tokens[0]

    def key_fn(p : Page):
        attr = p.__dict__[field]
        if isinstance(attr, str):
            attr = attr.lower()
        return attr

    return sorted(pages, key=key_fn, reverse = (tokens[1] == 'desc'))

def sort_pages(pages : list[Page], sort_fn: Callable):
    return sorted(pages, key = sort_fn)

def parse(query_str : str):
    # {LIST, TABLE, JSON, CSV} AS {txt, json, csv}
    # WHERE {condition}
    raise NotImplementedError()

def main():
    index(".")

if __name__ == "__main__":
    main()