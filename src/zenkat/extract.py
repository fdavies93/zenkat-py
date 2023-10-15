import re
from pathlib import Path
from zenkat.objects import Heading, Link, ListItem, Match
from yaml import load, Loader

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


def get_heading_tree(title: str, document: str):
    # technically this pattern is wrong as it doesn't account for code blocks
    pattern = re.compile("^(#+)\s+(.*)", re.MULTILINE)
    cur_doc = document
    next_head = pattern.search(cur_doc)
    root = Heading(title,0)
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

def get_list_tree(title: str, document: str, todo_map: dict):    
    # find list items, groups are:
    # 1: number of whitespace characters before (indent level)
    # 2: the list heading itself -- format determines type
    # 3: (optional) a todo box
    # 4: the actual text of the item
    pattern = re.compile(r"^([ \t]*)(\*|\-|\d+\.)[ ]+(?:(\[.\])[ ]+)?(.*)", re.MULTILINE)
    cur_doc = document

    next_ls = pattern.search(cur_doc)
    root = ListItem(title, -1,"unordered",None)
    cur = root
    stack = []

    while next_ls is not None:
        next_level, bullet, todo, text = next_ls.groups()
        next_level = len(next_level)

        links = get_all_links(text)
        # get type and status from bullet
        # could be its own function
        status = None
        if todo is not None and len(todo) > 0:
            li_type = "task"
            status = todo_map.get(todo[1])
            if status == None: status = "unknown"
        elif bullet[0] in "-*": li_type = "unordered"
        else: li_type = "ordered"            
        
        next = ListItem(text,next_level,li_type,status, links=links)
        while next_level <= cur.depth:
            cur = stack.pop()
        if next_level > cur.depth:
            cur.children.append(next)
            stack.append(cur)
            cur = next
        cur_doc = cur_doc[next_ls.end() + 1:]
        next_ls = pattern.search(cur_doc)

    return root

def get_lists(document: str, todo_map: dict):
    # find list items, groups are:
    # 1: number of whitespace characters before (indent level)
    # 2: the list heading itself -- format determines type
    # 3: (optional) a todo box
    # 4: the actual text of the item
    pattern = re.compile(r"^([ \t]*)(\*|\-|\d+\.)[ ]+(?:(\[.\])[ ]+)?(.*)", re.MULTILINE)
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
