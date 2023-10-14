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
from copy import deepcopy
from functools import reduce
from zenkat.objects import Tag, Link, Page, Heading, Match, ListItem, Task, Index
from zenkat.extract import get_headings, get_heading_tree, get_header_metadata, get_lists, get_all_links, get_word_count, get_tags


def node_tree_dft(root, child_property: str, do_fn: Callable[[object],bool]):
    '''
    Perform a depth first traversal of a node tree of objects and call do_fn at each node. If do_fn returns False, don't continue to navigate that branch of the tree.
    '''
    # perform a Depth First Traversal of a node tree and do something at each node
    outcome = do_fn(root)
    if not outcome:
        return False
    children = root.__dict__[child_property]
    for child in children:
        node_tree_dft(child, child_property, do_fn)
    return True
    
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
    
def index(path : str, config : dict, exclude : list = []):
    
    pages: list[Page] = []
    links_out: list[Link] = []
    tags: list[Tag] = []
    list_items: list[ListItem] = []
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

        headings = get_headings(document)
        cur_page.headings = headings
        heading_tree = get_heading_tree(title,document)
        cur_page.heading_tree = heading_tree

        metadata = get_header_metadata(document)
        cur_page.metadata = metadata

        lists = get_lists(document, config["formats"]["task_map"])
        for l in lists:
            for li in l:
                li.doc_abs_path = abs
                li.doc_title = title
                list_items.append(li)
        cur_page.lists = lists

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
            
    return Index(pages, tags, links_out, list_items)

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

def get_field_simple(obj, field: str):
    if type(obj) == list:
        obj_dict = { str(i): el for i, el in enumerate(obj) }
    elif type(obj) == dict:
        obj_dict = obj
    else:
        # it's probably a dataclass
        obj_dict = obj.__dict__

    return obj_dict.get(field)

def get_field_fn(root, field_name: str):
    parts = field_name.split(".")
    obj = root
    for i, part in enumerate(parts):
        # * for reduce
        field = get_field_simple(obj, part)
        
        if field == None and type(obj) == list:
            if part == "*":
                field = reduce(lambda acc, o: acc + o, obj, [])
            else:                
                field = list(map(lambda o : get_field_simple(o, part), obj))
        obj = field
    return obj

def format_list(objs : list[Any], f_str : str):
    outputs = []
    pattern = "{([\w\.\*&]+)}"    
    for o in objs:
        templates = re.findall(pattern, f_str)
        replacements = [get_field_fn(o,t) for t in templates]
        cur_str = re.sub(pattern, "{}", f_str)
        cur_str = cur_str.format(*replacements)                    
        outputs.append(cur_str)
        
    return outputs

def get_operator(op_str):
    operator_map = {
        '=': lambda a, b : a == b,
        '~': lambda a, b : a != b,
        'has': lambda a, b : b in a,
        '~has': lambda a, b : b not in a,
        '>': lambda a, b : a > b,
        '<': lambda a, b : a < b,
        '>=': lambda a, b : a >= b,
        '<=': lambda a, b : a <= b
    }
    return operator_map[op_str]

def convert_to_type(input_str, type_info):
    if type_info == datetime:
        output = convert_date_str(input_str)
    elif type_info == int:
        output = int(input_str)
    elif type_info == str:
        output = input_str
    else:
        output = input_str # sets could potentially use a lisp        
    return output

def parse_filter(filter_str: str, data_type):
    tokens = filter_str.split() # 'lexing' the filter
    
    set_transform = None
    if tokens[0] in ("any","all"):
        set_transform = tokens[0]
        tokens = tokens[1:]

    # get fields from object
    field_specifier = tokens[0]

    operation = get_operator(tokens[1])

    tokens[2] = " ".join(tokens[2:])

    def filter_fn(o):
        # get field values
        field = get_field_fn(o, field_specifier)
        # convert comparator to correct type based on field
        comparator = convert_to_type(tokens[2], type(field))
        # get operation
        my_op = operation
        
        if set_transform is not None:
            truth_vals = [my_op(f,comparator) for f in field]
            if len(truth_vals) == 0: return False
            if set_transform == "any": result = any(truth_vals)
            elif set_transform == "all": result = all(truth_vals)
            return result

        result = my_op(field, comparator)
        return result

    return filter_fn

@dataclass
class QueryData:
    results: list = field(default_factory=list)
    format_type: str = ""
    format_str: str = ""
    corpus: str = ""

def parse_query(query: str, index: Index) -> QueryData:
    clauses = {
        "format": [],
        "where": [],
        "sort": []
    }
    cur_clause = "format"
    acc = []
    # split into clauses
    words = query.split()
    for word in words:
        if word.lower() in clauses:
            clauses[cur_clause] = acc
            cur_clause = word.lower()
            acc = []
            continue
        acc.append(word)
    if len(acc) > 0: clauses[cur_clause] = acc

    output = QueryData()
    # get collection
    if len(clauses["format"]) < 2: raise ValueError("Format clause must have 2 or more arguments. e.g. list pages")
    output.format_type = clauses["format"][0]
    output.corpus = clauses["format"][1]
    data = index.__dict__.get(clauses["format"][1])
    if data == None: raise ValueError(f"No collection called {clauses[1]}!")
    if len(clauses["format"]) > 2: output.format_str = " ".join(clauses["format"][2:])
    # filter by objs
    if len(clauses["where"]) != 0 and len(data) > 0:
        if len(clauses["where"]) not in (3,4): raise ValueError("Filter clause must have 3-4 arguments. e.g. where rel_path has business")
        filter = parse_filter(" ".join(clauses["where"]), data[0])
        data = filter_objs(data, [filter])
    if len(clauses["sort"]) != 0:
        if len(clauses["sort"]) != 2: raise ValueError("Sort clause must have 2 arguments e.g. sort word_count asc")
        data = sort_from_query(data, " ".join(clauses["sort"]))

    output.results = data
    return output

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
        attr = get_field_fn(o, field)
        if isinstance(attr, str):
            attr = attr.lower()
        return attr

    return sorted(objs, key=key_fn, reverse = (tokens[1] == 'desc'))