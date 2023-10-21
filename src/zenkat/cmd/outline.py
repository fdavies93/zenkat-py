from rich.console import Console
from zenkat import index, utils, objects, filter
from argparse import ArgumentParser
from dataclasses import dataclass

@dataclass
class OutlineFilterObj:
    heading = objects.Heading
    page = objects.Page

def make_outline_parser(parser: ArgumentParser):
    parser.add_argument('--path', type=str, default='.')
    parser.add_argument("--filter","-f")

def outline(args, console: Console, config: dict):
    idx = index.index(args.path, config)

    outline = config["formats"]["outline"]

    root_tag, body_tag, spacer_tag, spacer, spacer_end = [outline[v] for v in ("root_tag","body_tag","spacer_tag","spacer","spacer_end")]

    filters = []
    if args.filter != None:
        filter_str = args.filter
        filters = [filter.parse_filter_str(filter_str, OutlineFilterObj)]
    
    for page in idx.pages:
        def print_node(node: objects.Heading):
            filter_obj = OutlineFilterObj()
            filter_obj.heading = node
            filter_obj.page = page
            # this filter should be over a dict including page and heading
            for f in filters:
                if not f(filter_obj): return True
        
            output = ""
            bt = body_tag
            if node.depth == 0: 
                bt = root_tag
            output += spacer_tag[0] + (node.depth * spacer) + spacer_end + spacer_tag[1] + bt[0] + node.text + bt[1]

            console.print(output)
        
            return True
        utils.node_tree_dft(page.heading_tree, "children", print_node)
