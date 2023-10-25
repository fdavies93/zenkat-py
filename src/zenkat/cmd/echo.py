import zenkat.format
from argparse import ArgumentParser

def make_echo_parser(parser: ArgumentParser):
    parser.add_argument("string")

def echo(args, console, conf):
        
    out = zenkat.format.format(args.string, {"test": "Hello world!"}, console, conf["theme"]["colors"])
    print(out)