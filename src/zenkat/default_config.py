default_config = {
    "theme": {
        "colors": {
            "alert": "red",
            "info": "bold green",
            "info2": "magenta",
            "main": "white bold",
            "link": "blue underline",
            "sub": "white default",
            "status": "yellow bold",
        },
        "tasks": {
            "page_format": "{:main:} {{ title }} {:end:} ({:link:}{{rel_path}}{:end:}) ",
            "task_format": "{{spacer}}{{spacer_head}}{{status_symbol}} {:{{status_style}}:}{{text}}{: end :}",
            "symbols": {
                "done": "✅",
                "not done": "⬜",
                "in progress": "⏳",
                "cancelled": "🚫",
                "blocked": "🔴",
                "unknown": "❓"
            },
            "metadata": {
                "due": "⏰",
                "priority": "🚩"
            },
            "styles": {
                "done": ["i","strike"],
                "not done": ["white"],
                "cancelled": ["red","strike","i"],
                "blocked": ["red"]
            },
            "spacer":" ",
            "spacer_end": "",
        }
    },
    "formats": {
        "default": {
            "list": {
                "pages": "{: info :}[↓{{in_link_count}} ↑{{out_link_count}}] {: end info :}{: main :}{{title}}{: end main :}, {: sub :}{{word_count}} words ({: link reset :}{{rel_path}}{: end link :}){: end sub :}",
                "links": "{: link :}{{doc_abs_path}}{: end :} => {: link :}{{href_resolved}}{: end :}",
                "tags": "{: info :}[{{count}} pages]{: end info :} {:main:}{{name}}{: end main :}",
            }
        },
        "outline": {
            "root_tag": ("[info]","[/info]"),
            "body_tag": ("[main]","[/main]"),
            "spacer_tag": ("",""),
            "spacer": "--",
            "spacer_end": "> "
        },
        "task_map": {
            " ": "not done",
            "x": "done",
            "/": "in progress",
            "~": "cancelled",
            "-": "blocked",
        }
    },
    "macros": {
        "list_pages": "list pages --sort 'word_count asc'",
        "stack_overflow": "macro stack_overflow",
        "demo": "\n".join([
            "echo '",
            "{:alert:}Alert sample{:end:}",
            "{:info:}Info sample{:end:}",
            "{:info2:}Info 2 sample{:end:}",
            "{:link:}Link sample{:end:}",
            "{:main:}Main sample{:end:}",
            "{:sub:}Sub sample{:end:}",
            "{:status:}Status sample{:end:}'",
        ]),
        
    },
    "queries": {
        "list": "list pages"
    }
}
