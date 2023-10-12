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
            "tags": {
                "done": ["[strike][i]","[/i][/strike]"],
                "cancelled": ["[alert][strike][i]","[/i][/strike][/alert]"],
                "blocked": ["[alert]","[/alert]"]
            }
        }
    },
    "formats": {
        "default": {
            "list": {
                "pages": "[info][↓{in_link_count} ↑{out_link_count}][/info] [main]{title}[/main], [sub]{word_count} words ([link]{rel_path}[/link])[/sub]",
                "links": "[link]{doc_abs_path}[/link] → [link]{href_resolved}[/link]",
                "tags": "[info][{count} pages][/info] [main]{name}[/main]",
                "list_items": "[link]{doc_title}[/link]\n[info]({type})[/info] {text}"
            }
        },
        "task_map": {
            " ": "not done",
            "x": "done",
            "/": "in progress",
            "~": "cancelled",
            "-": "blocked",
        },
        "outline": "[info]{title}[/info]\n{outline}"
    },
    "macros": {
        "list_pages": "list pages --sort 'word_count desc'",
        "stack_overflow": "macro stack_overflow"
    },
    "queries": {
    }
}
