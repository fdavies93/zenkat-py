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
class Tag:
    name: str
    count: int
    docs: set[str] = field(default_factory=set)

@dataclass()
class Link:
    '''
    Links don't really make sense outside of the context of a document. 
    '''
    text: str
    href: str
    href_resolved: str = ""
    doc_abs_path: str = ""
    type: str = ""
    
@dataclass()
class Page:
    title: str
    filename: str
    abs_path: str
    rel_path: str
    created_at: datetime
    modified_at: datetime
    tags: set[str] = field(default_factory=set)
    out_links: list[Link] = field(default_factory=list)
    out_link_count: int = 0
    in_links: list[Link] = field(default_factory=list)
    in_link_count: int = 0

@dataclass
class Index:
    pages: list[Page]
    tags: list[Tag]
    links: list[Link]

def get_tags(document: str):
    matches = re.findall("(?:^|\s)#([-_\w\d]+)",document)
    return set(matches)

def get_wiki_links(document : str) -> list[Link]:
    matches = re.findall("(?:^|\s)\[\[([#\/\-\w\s]+)\]\]", document)
    # in wiki-links, text and href are always the same
    links = [ Link(m,m,type="wiki") for m in matches ]
    return links

def get_regular_links(document: str) -> list[Link]:
    # captures links in format (text, url)
    # if you use the more involved .search process you can get index too :think:
    matches = re.findall("(?:^|\s)\[(.+)\]\(([\w\s/:#\-_.]+)\)", document)
    links = [ Link(m[0], m[1], type="regular") for m in matches ]
    return links

def get_all_links(document: str):
    all_links = []
    all_links.extend(get_wiki_links(document))
    all_links.extend(get_regular_links(document))
    return all_links
    

def resolve_links(links : list[Link], path : Path):
    out = []
    for l in links:
        # probably need to check if it's a uri or a local link
        # uri cannot be resolved
        matches = list(path.glob(f"{l.href}.*"))
        if len(matches) > 0:
            # ignores multiple matches rather than throwing error
            out.append(Link(
                text = l.text,
                href = l.href,
                doc_abs_path = l.doc_abs_path,
                href_resolved = str(matches[0].resolve()),
                type = l.type
            ))

    return out
    
def index(path : str, exclude : list = []):
    
    pages: list[Page] = []
    links_out: list[Link] = []
    tags: list[Tag] = []
    
    link_dests: dict[str,list[Link]] = dict()
    
    for p in Path(path).rglob("*.md"):
        suffixes = set(p.suffixes)
        if len(suffixes.intersection(exclude)) > 0:
            continue
        
        abs = str(p.absolute())

        path_obj = p
        while path_obj.suffix: path_obj = path_obj.with_suffix("")
        title = path_obj.name
        
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

        links = get_all_links(document)
        for l in links: l.doc_abs_path = str(p.absolute())
        # need to change how this works to more of an enrich link
        cur_page.out_links = resolve_links(links, p.parent)
        links_out.extend(cur_page.out_links)
        cur_page.out_link_count = len(cur_page.out_links)
        # add to absolute path dict
        for l in cur_page.out_links:
            if l.href_resolved not in link_dests:
                link_dests[l.href_resolved] = []
            link_dests[l.href_resolved].append(l)
        
        pages.append(cur_page)

    # calculate backlinks
    for page in pages:
        if page.abs_path in link_dests:
            page.in_links = link_dests[page.abs_path]
            page.in_link_count = len(link_dests[page.abs_path])
    
    return Index(pages, tags, links_out)

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