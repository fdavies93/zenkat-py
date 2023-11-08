from zenkat import fields
from dataclasses import dataclass
import re
from typing import Union
from copy import deepcopy
from rich.markdown import Markdown
from rich.console import Console
from zenkat.utils import node_tree_dft
from zenkat.group import GroupedListItem

# figure out process for rendering ALL segments of a string from a format string via rich and later assembling them
# USE OWN TEMPLATING LANGUAGE / JINJA LIKE SYNTAX
# 1st pass -> build an AST of the stuff to render -> named blocks. E.g. <alert> </alert>. Each block is rendered separately as markdown with styles defined in the named block.This avoids writing a separate MD parser. 
# 2nd pass -> use rich / other console color library to generate console codes for the stuff you want to render

# styles {: :}
# variables {{ }}

# also need to support named styles from config

@dataclass
class Block:
    styles: list[str]
    children: list[Union[str,"Block"]] 

def replace_from(obj, f_str: str):
    
    pattern = "{{\s*(.*?)\s*}}"    
    templates = re.findall(pattern, f_str)
    replacements = [fields.get_field_fn(obj,t) for t in templates]

    new_str = ""
    start_i = 0
    cur_tag = 0
    for match in re.finditer(pattern, f_str):
        before = f_str[start_i:match.start()]
        new_str += before
        start_i = match.end()
        if replacements[cur_tag] != None:
            new_str += str(replacements[cur_tag])
        cur_tag += 1

    before = f_str[start_i:]
    new_str += before
        
    return new_str

def lex_styles(f_str):
    pattern = re.compile("{:(.*?):}")
    matches = pattern.finditer(f_str)

    tokens = []

    last_i = 0
    
    for match in matches:
        tag = match.group(0)
        before = f_str[last_i:match.start()]

        if len(before) > 0: tokens.append(before)

        tokens.append(tag)
        
        last_i = match.end()

    if last_i < len(f_str):
        tokens.append(f_str[last_i:])

    return tokens

def parse_styles(tokens: list[str], styles = set()) -> tuple[Block, list[str]]:

    # PEG
    # block := { tag+ }? ~ (block | string)* ~ { end tag+ }?

    cur_styles = styles
    pattern = re.compile("{:(.*?):}")
    children: list[Union[Block, str]] = []
    remaining = deepcopy(tokens)
    
    while len(remaining) > 0:
        # break if you discover an end tag
        next = remaining[0]
        next_match = pattern.match(next)
        
        if next_match is not None:
            # i.e. it's a tag        
            style_names = next_match.group(1).split()
            # allows end tag to have syntactic sugar names
            if len(style_names) > 0 and style_names[0] == "end":
                remaining = remaining[1:]
                break

            child_styles = set(style_names)
            if "reset" not in child_styles:
                child_styles = child_styles.union(styles)
            else: child_styles.remove("reset")
            # include the starting tag so that the child can set its styles from it
            child = parse_styles(remaining[1:], child_styles)
            children.append(child[0])
            remaining = child[1]
            continue
        
        # i.e. it's just a string
        children.append(next)
        remaining = remaining[1:]            

    return (Block(cur_styles, children), remaining)

def combine_shortname_styles(styles: set[str], short_names: dict):
    output_styles: set(str) = set()
    for s in styles:
        if s in short_names:
            short = short_names[s]
            if isinstance(short, str): short = short.split()
            output_styles = output_styles.union(short)
            continue
        output_styles.add(s)
    return output_styles

def render_to_console_str(root: Block, console: Console, short_names: dict = {}) -> str:
    output_str = ""

    for segment in root.children:
        if isinstance(segment, Block):
            output_str += render_to_console_str(segment, console, short_names)
        elif isinstance(segment, str):
            # needs to expand styles with shortname

            styles = combine_shortname_styles(set(root.styles), short_names)

            i = 0
            whitespace_l = ""
            while i < len(segment) and segment[i] in "\n\t\r ":
                whitespace_l += segment[i]
                i += 1

            i = len(segment)-1
            whitespace_r = ""
            while i >= 0 and segment[i] in "\n\t\r ":
                whitespace_r = segment[i] + whitespace_r
                i -= 1
          
            md = Markdown(segment, style=" ".join(styles))
            # md = segment
            with console.capture() as cap:
                console.print(md, end="", sep="")
            rendered: str = cap.get()
            rendered = " ".join(rendered.split())
            # # restore whitespace prior to render
            rendered += whitespace_r
            if whitespace_l != whitespace_r:
                rendered = whitespace_l + rendered
            
            output_str = "".join( (output_str, rendered ) )
            output_str = output_str
    
    return output_str
    

def format(f_str, obj, console: Console, short_names: dict):
    replaced = replace_from(obj, f_str)
    lexed = lex_styles(replaced)
    parsed = parse_styles(lexed)
    rendered = render_to_console_str(parsed[0], console, short_names)
    return rendered


def format_list(objs : list, f_str : str, console: Console, short_names: dict):
    outputs = [format(f_str, obj, console, short_names) for obj in objs]
    return outputs

def format_grouped_list(f_str: str, gf_str: str, grouped_list: list[GroupedListItem], console: Console, short_names: dict):
    ls: list[str] = []
    seen: set[str] = set()
    # list should be pre-flattened
    for li in grouped_list:
        if li.group_value not in seen:
            ls.append(format(gf_str, li, console, short_names)) 
            seen.add(li.group_value)
        ls.append(format(f_str, li.obj, console, short_names))
    return ls
