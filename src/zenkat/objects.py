from dataclasses import dataclass, field
from datetime import datetime
from typing import Union

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

@dataclass
class Heading:
    '''
    Metadata about a heading on a page, used for outlines.
    '''
    text: str
    depth: int
    children: list = field(default_factory=list)

@dataclass
class ListItem:
    text: str
    depth: int
    type: str # ordered, unordered, task
    status: Union[str, None] # None, done, not done, in progress, blocked, cancelled
    children: list = field(default_factory=list)
    doc_abs_path: str = ""

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
    heading_tree: Heading = None
    lists: list = field(default_factory=list)
    lists_tree: ListItem = None

@dataclass
class Match:
    context: str
    line_no: int


@dataclass
class Task:
    # when filtering tasks, act like a redirect
    # from the user's perspective they're filtering
    # on a property called 'task'
    # actually, they're intervening in the method used
    # to return nested lists from a page and culling
    # nodes which don't pass the filter
    # what task actually returns is an n-tree for each document
    task: ListItem
    linked_page: Page

@dataclass
class Index:
    '''
    Object containing all other types of document.
    '''
    pages: list[Page]
    tags: list[Tag]
    links: list[Link]
    list_items: list[ListItem]
