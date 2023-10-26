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
            "repr.number": "white default",
            "repr.str": "white default",
            "repr.path": "white default"
        },
        "tasks": {
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
            "spacer_tag": ("", ""),
            "spacer": " ",
            "spacer_end": "",
            "page_title_tag": ("[info]", "[/info]"),
            "page_link_tag": ("[link]", "[/link]")
        }
    },
    "formats": {
        "default": {
            "list": {
                "pages": "{: info :}[↓{{in_link_count}} ↑{{out_link_count}}] {: end info :}{: main :}{{title}}{: end main :}, {: sub :}{{word_count}} words ({: link reset :}{{rel_path}}{: end link :}){: end sub :}",
                "links": "{: link :}{{doc_abs_path}}{: end link :} → {: link :}{{href_resolved}}{: end link :}",
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
        "stack_overflow": "macro stack_overflow"
    },
    "queries": {
        "list": "list pages"
    }
}
