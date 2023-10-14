from zenkat.cmd.utils import create_parser, get_cmd_map
import shlex

def macro(args, console, config):
    macro_name = args.command[1]
    macro_str = config["macros"][macro_name]
    macro_arg_str = shlex.split(macro_str)
    parser = create_parser()
    cmd_map = get_cmd_map()

    macro_args = parser.parse_args(macro_arg_str)

    if args.recursive == None:
        cmd_map[macro_args.command[0]](macro_args, console, config)    
        return
    
    wait_time = float(args.recursive)
    while True:
        console.clear()
        cmd_map[macro_args.command[0]](macro_args, console, config)    
        time.sleep(wait_time)
