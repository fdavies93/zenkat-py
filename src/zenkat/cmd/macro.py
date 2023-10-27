from zenkat.cmd.utils import create_parser, get_cmd_map
import shlex
import time
from argparse import ArgumentParser

def make_macro_parser(parser: ArgumentParser):
    parser.add_argument("name", nargs="?")
    parser.add_argument("--recursive","-r")

def macro(args, console, config):
    macro_name = args.name

    if macro_name == None:
        print("\n".join(config["macros"].keys()))
        return

    macro_str = config["macros"][macro_name]
    macro_arg_str = shlex.split(macro_str)
    parser = create_parser()
    cmd_map = get_cmd_map()

    macro_args = parser.parse_args(macro_arg_str)

    if args.recursive == None:
        cmd_map[macro_args.command](macro_args, console, config)    
        return
    
    wait_time = float(args.recursive)
    while True:
        console.clear()
        cmd_map[macro_args.command](macro_args, console, config)    
        time.sleep(wait_time)
