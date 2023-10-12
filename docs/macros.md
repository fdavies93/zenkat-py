# Macros

From v0.1.1 ZenKat includes the macro feature. You can put a macro in your `config.toml` and run any other zenkat command quickly:

```toml
[macros]
list_pages = "list pages --sort 'word_count desc'"
```

```sh
zenkat macro list_pages
```

You can also run using the -r command with a time increment. This will put the macro in *recursive mode*, which calls the macro repeatedly at the interval you specify. This may be helpful for displaying a sidebar. For example:

```toml
[macros]
tasks_not_done = "tasks --filter 'status = not done'"
```

```sh
zenkat macro tasks_not_done -r 5
```