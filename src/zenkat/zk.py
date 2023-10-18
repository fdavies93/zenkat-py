from zenkat import config, cmd
import sys
from rich.console import Console
from rich.theme import Theme
from rich.markdown import Markdown

def main():
    parser = cmd.utils.create_parser()
    args = parser.parse_args()

    cmd_map = cmd.utils.get_cmd_map()

    conf = config.load_config()
    console = Console(theme=Theme(conf["theme"]["colors"]))

    cmd_map[args.command](args, console, conf)
    
if __name__ == "__main__":
    sys.exit(main())