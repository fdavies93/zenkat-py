from rich.console import Console
from zenkat import index, utils, objects
import zenkat.filter
from argparse import ArgumentParser

def make_outline_parser(parser: ArgumentParser):
    parser.add_argument('--path', type=str, default='.')
    parser.add_argument("--filter","-f")

def outline(args, console: Console, config: dict):
    idx = index.index(args.path, config)

    outline = config["formats"]["outline"]

    root_tag, body_tag, spacer_tag, spacer, spacer_end = [outline[v] for v in ("root_tag","body_tag","spacer_tag","spacer","spacer_end")]

    filter_strs = []
    if args.filter != None:
        filter_strs = args.filter

    filters = [zenkat.filter.parse_filter(f, objects.Heading) for f in filter_strs]
    
    def print_node(node: objects.Heading):
        for f in filters:
            if not f(node): return False
        
        output = ""
        bt = body_tag
        if node.depth == 0: 
            bt = root_tag
        output += spacer_tag[0] + (node.depth * spacer) + spacer_end + spacer_tag[1] + bt[0] + node.text + bt[1]

        console.print(output)
        
        return True

    for page in idx.pages:
        utils.node_tree_dft(page.heading_tree, "children", print_node)
