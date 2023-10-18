import argparse
import zenkat.cmd as cmd
from zenkat.cmd.list import make_ls_parser
from zenkat.cmd.tasks import make_task_parser
from zenkat.cmd.grep import make_grep_parser
from zenkat.cmd.query import make_query_parser
from zenkat.cmd.outline import make_outline_parser
from zenkat.cmd.cat import make_cat_parser

def create_parser():
    
    parser = argparse.ArgumentParser(prog="zenkat", description="Zenkat: Library and CLI to use plain markdown files as a Zettelkasten knowledge store.")
    # parser.add_argument('command', nargs="+", help=cmd_help)
    command_parser = parser.add_subparsers(title="command", dest="command")
    command_parser.required = True
    list_parser = command_parser.add_parser("list")
    make_ls_parser(list_parser)
    
    task_parser = command_parser.add_parser("tasks")
    make_task_parser(task_parser)

    grep_parser = command_parser.add_parser("grep")
    make_grep_parser(grep_parser)
    
    query_parser = command_parser.add_parser("query")
    make_query_parser(query_parser)
    
    outline_parser = command_parser.add_parser("outline")
    make_outline_parser(outline_parser)
    
    cat_parser = command_parser.add_parser("cat")
    make_cat_parser(cat_parser)
    
    from zenkat.cmd.macro import make_macro_parser
    # macros call create_parser so this would be recursive if not imported inline
    macro_parser = command_parser.add_parser("macro")
    make_macro_parser(macro_parser)
    return parser

def get_cmd_map():
    return {
        'list': cmd.ls,
        'cat': cmd.cat,
        'grep': cmd.grep,
        'query': cmd.query,
        'tasks': cmd.tasks,
        'macro': cmd.macro,
        'outline': cmd.outline
    }
