from argparse import ArgumentParser
from dataclasses import dataclass, field, asdict, fields
import os
from datetime import datetime
from pathlib import Path, PosixPath
from typing import Any, Callable, Union
import re
from functools import cmp_to_key
from operator import attrgetter
import dateutil.parser

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

@dataclass()
class Tag:
    name: str
    count: int
    docs: set[str] = field(default_factory=set)

@dataclass()
class Link:
    '''
    Links don't really make sense outside of the context of a document. 
    '''
    doc_abs_path: str
    text: str
    index: int
    href: str
    href_resolved: str
    
def get_tags(document: str):
    matches = re.findall("(?:^|\s)#([-_\w\d]+)",document)
    return set(matches)

def get_wiki_links(document : str):
    matches = re.findall("(?:^|\s)\[\[([#\/\-\w\s]+)\]\]", document)
    # might want to resolve to an absolute path
    return set(matches)

def resolve_links(links : list[str], path : Path):
    out = []
    for l in links:
        matches = list(path.glob(f"{l}.*"))
        if len(matches) > 0:
            # ignores multiple matches rather than throwing error
            out.append(str(matches[0].absolute()))
    return out
    
def index(path : str, exclude : list = []):
    pages = []

    link_dests = dict()
    
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
        raw_links = get_wiki_links(document)
        cur_page.out_links = resolve_links(raw_links, p.parent)
        cur_page.out_link_count = len(cur_page.out_links)
        # add to absolute path dict
        for l in cur_page.out_links:
            if l not in link_dests:
                link_dests[l] = []
            link_dests[l].append(abs)
        
        pages.append(cur_page)

    # calculate backlinks
    for page in pages:
        if page.abs_path in link_dests:
            page.in_links = link_dests[page.abs_path]
            page.in_link_count = len(link_dests[page.abs_path])
    
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

def convert_date_str(date_str : str):
    return dateutil.parser.parse(date_str)

def generate_filter(filter_str : str, data_type):
    tokens = filter_str.split()
    field_name = tokens[0]
    operator = tokens[1]
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

    fs = fields(data_type)
    
    columns = [f for f in fs if f.name == field_name]
    if len(columns) == 0: raise ValueError()
    field_obj = columns[0]

    if field_obj.type == datetime:
        if operator == 'has': raise ValueError()
        tokens[2] = convert_date_str(tokens[2])
    elif field_obj.type == int:
        if operator == 'has': raise ValueError() 
        tokens[2] = int(tokens[2])
    elif field_obj.type == set:
        if operator != 'has': raise ValueError()

    return lambda p : fn(p.__dict__[tokens[0]], tokens[2])

def filter_objs(objs : list[Union[Page,Tag]], filters: list[Callable]):
    out = objs
    for f in filters:
        out = list(filter(f, out))
    return out
    
def sort_from_query(objs: list[Union[Page,Tag]], sort_str : str):
    tokens = sort_str.split()
    if tokens[1] not in ('asc','desc'):
        raise ValueError()

    field = tokens[0]

    def key_fn(o : Union[Page,Tag]):
        attr = o.__dict__[field]
        if isinstance(attr, str):
            attr = attr.lower()
        return attr

    return sorted(objs, key=key_fn, reverse = (tokens[1] == 'desc'))

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