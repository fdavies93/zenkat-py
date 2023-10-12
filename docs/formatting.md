# Formatting

You can format the output of zenkat by using a format string in Python format.

```
zenkat list pages --format "[↓{in_link_count} ↑{out_link_count}] {title}, {word_count} words ({rel_path})"

zenkat list links --format "{doc_abs_path} → {href_resolved}"
```

As of v0.0.10 formatting can make use of subfields of pages correctly in the same way as filter.

```
zenkat list pages --format "{title} {rel_path} {out_links.text} {in_links.doc_abs_path}"
```

As of v0.1 zenkat supports rich text using [the rich library](https://github.com/Textualize/rich). You can include rich tags in your format arguments. For example, this is the default page format:

```
[info][↓{in_link_count} ↑{out_link_count}][/info] [main]{title}[/main], [sub]{word_count} words ([link]{rel_path}[/link])[/sub]
```

The formatting for semantic tags like `[info]` and `[link]` can be edited in `config.toml` under `[theme.colors]`. The `/themes` folder of this repository gives some examples (feel free to contribute more!). For example, here's my favorite, monokai:

```toml
[theme.colors]
comment = "#797979"
white = "#d6d6d6"
yellow = "#e5b567"
green = "#b4d273"
orange = "#e87d3e"
purple = "#9e86c8"
pink = "#b05279"
blue = "#6c99bb"

alert = "#e5b567 bold"
info = "#e87d3e bold"
info2 = "#e5b567"
link = "#b4d273 underline"
main = "#d6d6d6 bold"
sub = "#d6d6d6"
status = "#b05279 bold"
```

As of v0.1 zenkat also supports shortcuts for formats with the `-F` flag. You can create these in `config.toml`.

```
# in config.toml
[formats]
outline = [info]{title}[/info]\n{outline}

# on the command line
zenkat list pages -F outline
```

Default options for `list` can also be configured:

```toml
[formats.default.list]
pages = "[info][↓{in_link_count} ↑{out_link_count}][/info] [main]{title}[/main], [sub]{word_count} words ([link]{rel_path}[/link])[/sub]"
links = "[link]{doc_abs_path}[/link] → [link]{href_resolved}[/link]"
tags = "[info][{count} pages][/info] [main]{name}[/main]"
list_items = "[link]{doc_title}[/link]\n[info]({type})[/info] {text}"
```
