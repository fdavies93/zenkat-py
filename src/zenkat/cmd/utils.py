import argparse
import zenkat.cmd as cmd

def create_parser():
    parser = argparse.ArgumentParser(prog="zenkat", description="Zenkat: Library and CLI to use plain markdown files as a Zettelkasten knowledge store.")
    parser.add_argument('command', nargs="+")
    parser.add_argument('--path', nargs='?', const='.', type=str, default='.')
    parser.add_argument("-e","--exclude",action='append')
    parser.add_argument("--format")
    parser.add_argument("--quick-format","-F")
    parser.add_argument("--filter", "-f", action="append")
    parser.add_argument("--page")
    parser.add_argument("--sort", '-s')
    parser.add_argument("--query","-q")
    parser.add_argument("--recursive", "-r")
    parser.add_argument("--limit","-l")
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
