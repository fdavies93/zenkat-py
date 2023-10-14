from zenkat import zenkat
from rich.console import Console

def query(args, console: Console, config: dict):
    index = zenkat.index(args.path, config)
    if len(args.command) > 1 and config["queries"].get(args.command[1]) != None:
        query = config["queries"].get(args.command[1])
    elif args.query != None:
        query = args.query
    else:        
        raise ValueError("Must use the -q / --query flag when calling query or call a saved query from config.queries")
    output = zenkat.parse_query(query, index)

    corpus = output.corpus
    if corpus == "links":
        f_str = config["formats"]["default"]["list"]["links"]
        data = index.links
    elif corpus == "pages": 
        f_str = config["formats"]["default"]["list"]["pages"]
        data = index.pages
    elif corpus == "tags": 
        f_str = config["formats"]["default"]["list"]["tags"]
        data = index.tags
    elif corpus == "list_items":
        f_str = config["formats"]["default"]["list"]["list_items"]
        data = index.list_items
    else: raise ValueError()
    
    if output.format_str != "":
        f_str = output.format_str

    quick_format = args.quick_format
    if quick_format != None:
        f_str = config["formats"][quick_format]

    if args.format != None:
        f_str = args.format

    ls = zenkat.format_list(output.results, f_str)
    for line in ls:
        console.print(line)
