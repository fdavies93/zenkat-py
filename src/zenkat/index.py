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
from zenkat.objects import Tag, Link, Page, Heading, ListItem, Task, Index
from zenkat.extract import get_headings, get_heading_tree, get_header_metadata, get_lists, get_all_links, get_word_count, get_tags
import zenkat.fields as fields
    
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
