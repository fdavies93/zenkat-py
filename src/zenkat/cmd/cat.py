from pathlib import Path
from rich.console import Console
from rich.markdown import Markdown

def cat(args, console: Console, config: dict):
    path = args.command[1]
    p = Path(path)
    if (p.exists() and p.suffixes[-1] == ".md"):
        document = p.read_text()
        md = Markdown(document)
        console.print(md)
