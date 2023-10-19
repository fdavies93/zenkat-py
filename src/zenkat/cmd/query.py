import zenkat.query
import zenkat.format
from rich.console import Console
from argparse import ArgumentParser

def make_query_parser(parser: ArgumentParser):
    parser.add_argument('--path', type=str, default='.')
    parser.add_argument("--query-inline","-q")
    parser.add_argument("query", nargs="?")
    parser.add_argument("--quick-format","-F")
    parser.add_argument("--format")

def query(args, console: Console, config: dict):
    idx = zenkat.index.index(args.path, config)
    if args.query != None and config["queries"].get(args.query) != None:
        query_str = config["queries"].get(args.query)
    elif args.query_inline != None:
        query_str = args.query_inline
    else:        
        raise ValueError("Must use the -q / --query flag when calling query or call a saved query from config.queries")
    output = zenkat.query.parse_query(query_str, idx)

    corpus = output.corpus
    if corpus == "links":
        f_str = config["formats"]["default"]["list"]["links"]
        data = idx.links
    elif corpus == "pages": 
        f_str = config["formats"]["default"]["list"]["pages"]
        data = idx.pages
    elif corpus == "tags": 
        f_str = config["formats"]["default"]["list"]["tags"]
        data = idx.tags
    elif corpus == "list_items":
        f_str = config["formats"]["default"]["list"]["list_items"]
        data = idx.list_items
    else: raise ValueError()
    
    if output.format_str != "":
        f_str = output.format_str

    quick_format = args.quick_format
    if quick_format != None:
        f_str = config["formats"][quick_format]

    if args.format != None:
        f_str = args.format

    ls = zenkat.format.format_list(output.results, f_str)
    for line in ls:
        console.print(line)