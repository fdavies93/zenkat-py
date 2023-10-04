from argparse import ArgumentParser
from dataclasses import dataclass, field, asdict, fields
import os
from datetime import datetime
from pathlib import Path, PosixPath
from typing import Any, Callable, Union
import re
from functools import cmp_to_key
from operator import attrgetter
from typing import Iterable
import dateutil.parser


@dataclass()
class Tag:
    '''
    Metadata about a tag, including which pages it appears in as absolute (resolved) paths.
    '''
    name: str
    count: int = 0
    docs: set[str] = field(default_factory=set)

@dataclass()
class Link:
    '''
    A link from one page to another page or to an external uri.
    '''
    text: str
    href: str
    href_resolved: str = ""
    doc_abs_path: str = ""
    type: str = ""
    
@dataclass()
class Page:
    '''
    Metadata about a single text file.
    '''
    title: str
    filename: str
    abs_path: str
    rel_path: str
    created_at: datetime
    modified_at: datetime
    tags: list[Tag] = field(default_factory=list)
    out_links: list[Link] = field(default_factory=list)
    out_link_count: int = 0
    in_links: list[Link] = field(default_factory=list)
    in_link_count: int = 0
    word_count: int = 0

@dataclass
class Index:
    '''
    Object containing all other types of document.
    '''
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
    
def get_word_count(document: str):
    words = document.split()
    return len(words)

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
    page_paths: dict[str, Page] = dict()
    link_dests: dict[str,list[Link]] = dict()
    tag_names: dict[str, Tag] = dict()
    
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

        links = get_all_links(document)
        for l in links: l.doc_abs_path = str(p.absolute())
        # need to change how this works to more of an enrich link
        cur_page.out_links = resolve_links(links, p.parent)
        links_out.extend(cur_page.out_links)
        cur_page.out_link_count = len(cur_page.out_links)
        cur_page.word_count = get_word_count(document)
        # add to absolute path dict
        for l in cur_page.out_links:
            if l.href_resolved not in link_dests:
                link_dests[l.href_resolved] = []
            link_dests[l.href_resolved].append(l)

        for tag in get_tags(document):
            if tag_names.get(tag) == None:
                tag_names[tag] = Tag(tag)
            tag_names[tag].docs.add(abs)
            tag_names[tag].count += 1

        page_paths[cur_page.abs_path] = cur_page
        pages.append(cur_page)

    # append tags to pages
    for tag_name, tag_obj in tag_names.items():
        pages_w_tag = tag_obj.docs.intersection(page_paths.keys())
        for page_path in pages_w_tag:
            page_paths[page_path].tags.append(tag_obj)
    
    # calculate backlinks
    for link_dest, link_obj in link_dests.items():
        if link_dest not in page_paths: continue
        page_paths[link_dest].in_links = link_obj
        page_paths[link_dest].in_link_count = len(link_obj)

    tags = [t for t in tag_names.values()]
            
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

def convert_input_to_field(data_type, input_str: str, field_name: str):
    '''
    Given a data_type, which must be a dataclass instance or class, convert the input str to be the same type as the field designated by name
    ''' 

    fs = fields(data_type)

    
    columns = [f for f in fs if f.name == field_name]
    if len(columns) == 0: raise ValueError()
    field_obj = columns[0]

    if field_obj.type == datetime:
        output = convert_date_str(input_str)
    elif field_obj.type == int:
        output = int(input_str)
    elif field_obj.type == str:
        output = input_str
    else:
        raise NotImplementedError()
    return output
        

def generate_filter(filter_str : str, data_type):
    tokens = filter_str.split()
    field_name = tokens[0]

    split_field = field_name.split(".")

    # this is kinda turning into a parser
    if len(split_field) > 1:
        field_name = split_field[0]
        subfield_name = split_field[1]
    
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

    if len(split_field) > 1:
        def search_iter(p):
            iterable = p.__dict__[field_name]
            for el in iterable:
                compare_to = convert_input_to_field(el, tokens[2], subfield_name)
                # convert tokens[2] based on type of subfield
                subfield = el.__dict__[subfield_name]
                if el.__dict__[subfield_name] == tokens[2]:
                    return True
            return False
        return search_iter

    compare_to = convert_input_to_field(data_type, tokens[2], field_name)
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