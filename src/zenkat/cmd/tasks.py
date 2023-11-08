from zenkat import index
import zenkat.filter
import zenkat.objects
import zenkat.format
from zenkat.utils import node_tree_dft
from rich.console import Console, Group
from rich.style import Style
from rich.markdown import Markdown
from argparse import ArgumentParser
import dateutil
import datetime
from dataclasses import dataclass

@dataclass
class TaskRenderObj:
    text: str
    status_symbol: str
    spacer: str
    spacer_head: str
    status_style: str
    status_symbol: str
    due_str: str = ""
    priority_str: str = ""

@dataclass
class TaskFilterObj:
    page: zenkat.objects.Page
    task: zenkat.objects.ListItem

def make_task_parser(parser: ArgumentParser):
    parser.add_argument('--path', type=str, default='.')
    parser.add_argument("--filter","-f")
    parser.add_argument("--limit","-l")
    parser.add_argument("--page")

# TODO
# move resolution of links in list items to index function
# change rendering to use render module

def tasks(args, console: Console, config: dict):
    idx = index.index(args.path, config)
    # the first filter applies to the tasks
    # the second filter applies to the page
    # all others are ignored
    
    filter_str = ""
    if args.filter != None:
        filter_str = args.filter

    pages = idx.pages

    li_filter = None
    if len(filter_str) > 0:
        li_filter = zenkat.filter.parse_filter_str(filter_str, TaskFilterObj)

    status_symbols = config["theme"]["tasks"]["symbols"]
    status_styles = config["theme"]["tasks"]["styles"]
    spacer = config["theme"]["tasks"]["spacer"]
    spacer_end = config["theme"]["tasks"]["spacer_end"]
    metadata_symbols = config["theme"]["tasks"]["metadata"]
    page_format = config["theme"]["tasks"]["page_format"]
    task_format = config["theme"]["tasks"]["task_format"]
    short_names = config["theme"]["colors"]
 
    li_limit = 0
    if args.limit != None:
        li_limit = int(args.limit)
    
    li_no = 0
    li_els = []
        
    for p in pages:
        li_els = []
        # probably need a function factory for this at some point
        def do_fn(li: zenkat.objects.ListItem):
            
            filter_obj = TaskFilterObj(p, li)
            if li.depth < 0: return True
            if li.type != "task": return False
            if li_filter is not None and not li_filter(filter_obj):
                return True
            nonlocal li_no
            if li_limit > 0 and li_no > li_limit: return False

            due = None
            priority = None
            due_str = ""
            priority_str = ""
            status_str = ""
            status_symbol = status_symbols.get(li.status)

            if li.status in status_styles:
                status_str = " ".join(status_styles[li.status])

            nonlocal spacer, spacer_end
            spacer_str = spacer * li.depth
            # should this be created at index time and 'lifted' to the list item? yes.
            # but there shouldn't be a task item indexed because there's little reason to separate it from mainline lists
            for link in li.links:
                if priority is None and "priority" in link.linked_metadata:
                    priority = link.linked_metadata["priority"]
                if due is None and "due" in link.linked_metadata:
                    due = dateutil.parser.parse(link.linked_metadata["due"])
                if priority is not None and due is not None: break

            if due is not None:
                format_str = "%Y-%m-%d"
                if (due.hour != 0) or (due.minute != 0) or (due.second != 0) or (due.microsecond != 0):
                    format_str += " %I:%M %p"
                due_str = due.strftime(format_str)
                due_str += metadata_symbols['due']

            if priority is not None:
                priority_str = str(priority) + metadata_symbols['priority']

            render_obj = TaskRenderObj(text=li.text, spacer=spacer_str, spacer_head=spacer_end, status_style=status_str, status_symbol=status_symbol, due_str=due_str, priority_str=priority_str)
            li_els.append(render_obj)

            li_no += 1
            return True

        node_tree_dft(p.lists_tree, "children", do_fn)
        if len(li_els) == 0: continue

        # pass format string & page to this 
        page_rendered = zenkat.format.format(page_format, p, console, short_names)

        print(page_rendered)
        # pass 
        for el in li_els:
            formatted = zenkat.format.format(task_format, el, console, short_names)
            print(formatted)
