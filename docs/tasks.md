# Tasks

As of v0.1 zenkat supports task lists similar to the [Obsidian Tasks Plugin](https://github.com/obsidian-tasks-group/obsidian-tasks), albeit more limited.
```
zenkat tasks --filter "status = not done" --page "tags.name has business"
```

By default, all tasks from all pages are included. The `--filter` flag filters on task ListItems, while the `--page` flag filters on source pages.

You can configure the appearance of tasks in `config.toml`:

```toml
[tasks.symbols]
done = "✅"
not_done = "⬜"
in_progress = "⏳"
cancelled = "🚫"
blocked = "🔴"

[tasks.tags]
# need to specify opening and closing tags
done = ["[strike][i]","[/i][/strike]"]
cancelled = ["[alert][strike][i]","[/i][/strike][/alert]"]
blocked = ["[alert]","[/alert]"]
```
