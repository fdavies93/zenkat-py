from argparse import ArgumentParser
from zenkat.config import locate_themes, load_theme
from zenkat.format import format
from dataclasses import dataclass, field
from pathlib import Path

@dataclass
class ThemeData:
    name: str
    abs_path: str
    rel_path: str
    keys: dict = field(default_factory=dict)

def make_theme_parser(parser: ArgumentParser):
    # literally just reports themes
    parser.add_argument("name", nargs="?")

def themes(args, console, conf):
    theme_paths: List[Path] = locate_themes()
    theme_objs = []
    for p in theme_paths:
        data = ThemeData(
            p.stem, 
            str(p.absolute()), 
            str(p.relative_to(Path.home())),
            load_theme(p)["theme"]["colors"])
        theme_objs.append(data)


    short_names = conf["theme"]["colors"]

    if args.name == None:
        for obj in theme_objs:
            out_str = format(conf["formats"]["default"]["themes"]["list"], obj, console, short_names)
            print(out_str)
        return

    # else print all the keys styled as themselves
    theme = filter(lambda obj: obj.name == args.name, theme_objs).__next__()
    for key, val in theme.keys.items():
        out_str = format("{: {{ styles }} :}{{name}}{: end :}", {"styles": val, "name": key}, console, short_names)
        print(out_str)