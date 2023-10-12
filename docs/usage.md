# Usage

ZenKat supports a number of operations based on the fields it indexes. As of version v0.0.10 it indexes documents, links, list items, and tags and can recursively access properties. You can customise the output using `--format`.

```sh
zenkat list pages --filter "tags.name has writing" --format "{rel_path} {tags.name}"
```

One of the most powerful features of ZenKat is the ability to calculate backlinks and resolve paths:
```sh
zenkat list pages --sort "in_link_count asc"
```

It can correctly operate over dates using filters.

```sh
zenkat list pages --filter "created_at > Sep 25 2023"
```

You can also combine multiple filters, which will act like an AND statement.

```sh
zenkat list pages --filter "rel_path has business" --filter "rel_path has Client"
```

You can sort by fields using straightforward ascending / descending statements. Note that you can only sort on one field at the moment.

```sh
zenkat list pages --filter "rel_path has business" --sort "modified_at asc" --format "{modified_at} {filename}"
```

You can get a simple list of tags and then find which pages have those tags:

```sh
zenkat list tags
zenkat list pages --filter "any tags.name = daily"
```

You can access subfields recursively in most commands:
```sh
zenkat list pages --format "{title} {tags.0.name}"
```

You can keep track of your tasks and filter your todo lists:
```sh
zenkat tasks --filter "status ~ done"
```

You can quickly check document formatting:
```sh
zenkat cat README.md
```

You can store specific commands as macros from config:

```toml
[macros]
list_pages = "list pages --sort 'word_count desc'"
```

```sh
zenkat macro list_pages
```