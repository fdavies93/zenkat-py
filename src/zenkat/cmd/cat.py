from pathlib import Path
from rich.console import Console
from rich.markdown import Markdown
from argparse import ArgumentParser

def make_cat_parser(parser: ArgumentParser):
    parser.add_argument("path")

def cat(args, console: Console, config: dict):
    path = args.path
    p = Path(path)
    if (p.exists() and p.suffixes[-1] == ".md"):
        document = p.read_text()
        md = Markdown(document)
        console.print(md)
