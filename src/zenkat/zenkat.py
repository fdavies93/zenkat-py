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
from yaml import load, Loader
import tomllib
from copy import deepcopy
from functools import reduce
from zenkat.default_config import default_config

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
    doc_title: str = ""
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
    metadata: dict = field(default_factory=dict)
    headings: list = field(default_factory=list)
    outline: str = ""
    lists: list = field(default_factory=list)

@dataclass
class Heading:
    '''
    Metadata about a heading on a page, used for outlines.
    '''
    text: str
    depth: int
    children: list = field(default_factory=list)

@dataclass
class Match:
    context: str
    line_no: int

@dataclass
class ListItem:
    text: str
    depth: int
    type: str # ordered, unordered, task
    status: Union[str, None] # None, done, not done, in progress, blocked, cancelled
    children: list = field(default_factory=list)
    doc_abs_path: str = ""

@dataclass
class Index:
    '''
    Object containing all other types of document.
    '''
    pages: list[Page]
    tags: list[Tag]
    links: list[Link]
    list_items: list[ListItem]

def get_tags(document: str):
    matches = re.findall("(?:^|\s)#([-_\w\d\/]+)",document)
    out = set()
    for m in matches:
        for i, char in enumerate(m):
            if char == '/':
                out.add(m[:i])
        out.add(m)
    return out

def get_header_metadata(document: str):
    header = re.findall(r"(?:^---\n)((?:.|\n)*?)(?:---)",document)
    metadata = dict()
    if len(header) > 0:
        # uses default loader, which is slower than C version
        # but adds less dependencies
        metadata = load(header[0], Loader=Loader)
    return metadata

def get_headings(document: str):
    pattern = re.compile("^(#+)\s+(.*)", re.MULTILINE)
    matches = pattern.findall(document)
    return [Heading(m[1], len(m[0])) for m in matches]

def get_heading_tree(document: str):
    # technically this pattern is wrong as it doesn't account for code blocks
    pattern = re.compile("^(#+)\s+(.*)", re.MULTILINE)
    cur_doc = document
    next_head = pattern.search(cur_doc)
    root = Heading("Document",0)
    cur = root
    head_stack = []
    while next_head is not None:
        next_level = len(next_head.group(1))
        next_title = next_head.group(2)
        next = Heading(next_title, next_level)
        while next_level <= cur.depth:
            # return up tree until reaching good level
            cur = head_stack.pop()
        if next_level > cur.depth:
            # descend and push to stack
            cur.children.append(next)
            head_stack.append(cur)
            cur = next
        cur_doc = cur_doc[next_head.end() + 1:]
        next_head = pattern.search(cur_doc)
    
    return root

def get_lists(document: str, todo_map: dict):
    # find list items, groups are:
    # 1: number of whitespace characters before (indent level)
    # 2: the list heading itself -- format determines type
    # 3: (optional) a todo box
    # 4: the actual text of the item
    pattern = re.compile(r"^([ \t]*)(\*|\-|\d+\.)[ ]+(?:(\[.\])[ ]+)?(.*)")
    out = []
    cur_list = []
    
    last_ln = -1

    for ln_no, ln in enumerate(document.splitlines()):
        m = re.search(pattern, ln)
        if m is None: continue
        g = m.groups()
        # we don't care if it's tab or space, only number of chars
        indent_level, bullet, todo, text = len(g[0]), g[1], g[2], g[3]
        status = None
        if todo is not None and len(todo) > 0:
            li_type = "task"
            status = todo_map.get(todo[1])
            if status == None: status = "unknown"
        elif bullet[0] in "-*": li_type = "unordered"
        else: li_type = "ordered"            
        li = ListItem(text, indent_level, li_type, status)
        if ln_no != last_ln + 1 and len(cur_list) > 0:
            out.append(cur_list)
            cur_list = []
        cur_list.append(li)
        
        last_ln = ln_no

    if len(cur_list) > 0:
        out.append(cur_list)

    return out

def adjust_config(original, adjuster):
    new_config = deepcopy(original)
    for key in adjuster:
        k = new_config.get(key)
        ak = adjuster.get(key)
        # need to see how this plays out with lists
        if type(k) == dict and type(ak) == dict:
            new_config[key] = adjust_config(new_config[key], adjuster[key])
            continue
        new_config[key] = adjuster[key]
    return new_config

def load_config() -> dict:
    # load config from an escalating series of paths or default
    paths = [Path.home() / ".config/zenkat/config.toml"]
    # default settings
    config = default_config
    for path in paths:
        if not path.exists():
            continue
        with open(path, "rb") as f:
            new_config = tomllib.load(f)
        config = adjust_config(config, new_config)
    return config

def get_wiki_links(document : str) -> list[Link]:
    matches = re.findall("(?:^|\s)\[\[([#\/\-\w\s]+)\]\]", document)
    # in wiki-links, text and href are always the same
    links = []
    for m in matches:
        no_head_link = m.split("#")[0]   
        links_obj = Link(no_head_link, no_head_link, type="wiki")
        links.append(links_obj)
    return links

def get_regular_links(document: str) -> list[Link]:
    # captures links in format (text, url)
    # if you use the more involved .search process you can get index too :think:
    matches = re.findall("(?:^|\s)\[(.+)\]\(([\w\s/#\-_.]+)\)", document)
    
    links = []
    for m in matches:
        no_head_link = m[1].split("#")[0]   
        links_obj = Link(m[0], no_head_link, type="regular")
        links.append(links_obj)
    return links

def get_all_links(document: str):
    all_links = []
    all_links.extend(get_wiki_links(document))
    all_links.extend(get_regular_links(document))
    return all_links
    
def get_word_count(document: str):
    words = document.split()
    return len(words)

def grep(path, pattern):
    regexp = re.compile(pattern)
    document = Path(path).read_text()
    doc_lines = document.splitlines()

    matches = []
    for ln_no, ln in enumerate(doc_lines):
        out_ln = ""
        slice = ln
        next_match = regexp.search(slice)
        while next_match != None:
            before = slice[:next_match.start()]
            m_str = next_match.group(0)
            out_ln += "{}[info2]{}[/info2]".format(
                before,
                m_str
            )
            slice = slice[next_match.end():]
            next_match = regexp.search(slice)
        
        if out_ln != "":
            out_ln += slice
            matches.append(Match(out_ln, ln_no))
    return matches

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

        outlines = []
        for h in headings:
            outlines.append(f"{h.depth * '--'} [info2]{h.text}[/info2]")
        outline_str = "\n".join(outlines)
        cur_page.outline = outline_str

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

def get_content(page : Page):
    with open(page.abs_path, 'r') as f:
        content = f.read()
    return content


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

    return sorted(objs, key=key_fn, reverse = (tokens[1] == 'asc'))

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