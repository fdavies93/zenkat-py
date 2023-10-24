from zenkat import index
import zenkat.filter
import zenkat.objects
from zenkat.utils import node_tree_dft
from rich.console import Console, Group
from rich.style import Style
from rich.markdown import Markdown
from argparse import ArgumentParser
import dateutil
import datetime
from dataclasses import dataclass

@dataclass()
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
    spacer_tag = config["theme"]["tasks"]["spacer_tag"]
    spacer_end = config["theme"]["tasks"]["spacer_end"]
    page_title_tag = config["theme"]["tasks"]["page_title_tag"]
    page_link_tag = config["theme"]["tasks"]["page_link_tag"]
    metadata_symbols = config["theme"]["tasks"]["metadata"]

    li_limit = 0
    if args.limit != None:
        li_limit = int(args.limit)
    
    li_no = 0
    li_strs = []
        
    for p in pages:
        li_strs = []
        # probably need a function factory for this at some point
        def do_fn(li: zenkat.objects.ListItem):
            filter_obj = TaskFilterObj(p, li)
            if li.depth < 0: return True
            if li.type != "task": return False
            if li_filter is not None and not li_filter(filter_obj):
                return True
            nonlocal li_no, li_strs
            if li_limit > 0 and li_no > li_limit: return False
            sym = status_symbols.get(li.status)
            spacer_str = spacer_tag[0] + (spacer * li.depth) + spacer_end + spacer_tag[1]

            txt_style = "none"
            if li.status in status_styles:
                txt_style = " ".join(status_styles[li.status])
            txt = Markdown(li.text, style=txt_style)
        
            li_els = [f"{spacer_str}[status]{sym}[/status]", txt]

            due = None
            priority = None

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
                li_els.append(f"{metadata_symbols['due']}{due_str}")

            if priority is not None:
                li_els.append(f"{metadata_symbols['priority']}{priority}")

            rendered = []
            for i, el in enumerate(li_els):
                with console.capture() as c:
                    console.print(el)
                out_str = c.get().replace("\n","")
                rendered.append(out_str)

            li_strs.append(" ".join(rendered).rstrip())
            li_no += 1
            return True
        node_tree_dft(p.lists_tree, "children", do_fn)
        if len(li_strs) == 0: continue
        console.print(f"{page_title_tag[0]}{p.title}{page_title_tag[1]} ({page_link_tag[0]}{p.rel_path}{page_link_tag[1]})")
        for li_els in li_strs:
            print(li_els)