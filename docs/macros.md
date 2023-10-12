# Macros

From v0.1.1 ZenKat includes the macro feature. You can put a macro in your `config.toml` and run any other zenkat command quickly:

```toml
[macros]
list_pages = "list pages --sort 'word_count desc'"
```

```sh
zenkat macro list_pages
```
