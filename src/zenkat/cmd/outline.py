from rich.console import Console
from zenkat import zenkat

def outline(args, console: Console, config: dict):
    index = zenkat.index(args.path, config)

    outline = config["formats"]["outline"]

    root_tag, body_tag, spacer_tag, spacer, spacer_end = [outline[v] for v in ("root_tag","body_tag","spacer_tag","spacer","spacer_end")]

    filter_strs = []
    if args.filter != None:
        filter_strs = args.filter

    filters = [zenkat.parse_filter(f, zenkat.Heading) for f in filter_strs]
    
    def print_node(node: zenkat.Heading):
        for f in filters:
            if not f(node): return False
        
        output = ""
        bt = body_tag
        if node.depth == 0: 
            bt = root_tag
        output += spacer_tag[0] + (node.depth * spacer) + spacer_end + spacer_tag[1] + bt[0] + node.text + bt[1]

        console.print(output)
        
        return True

    for page in index.pages:
        zenkat.node_tree_dft(page.heading_tree, "children", print_node)
