[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0) ![PyPI - Downloads](https://img.shields.io/pypi/dm/zenkat)

# ZenKat

ZenKat is a tool and library to enable using a set of plaintext files, especially markdown files, as a [Zettelkasten](https://en.wikipedia.org/wiki/Zettelkasten) knowledge base.

I've used a number of knowledge management tools including Obsidian, Notion, and Coda, and have found them all lacking and / or designed in a way that makes them act as a walled garden. ZenKat is an attempt to create a lightweight FOSS alternative for command-line users. As such it aims to have few dependencies while still providing decent features.

It's named this way because of my bad memory for German. I remembered ZEttelKAsTen as ZenKat (unclear where the N came from).

![](images/zk-0-0-9-demo.gif)

## Recommended Setup

You can install directly from pip:

```
pip install zenkat
```

This also installs the `zenkat` convenience script.

If you'd like to run directly from source you can clone the repository and use [development mode](https://setuptools.pypa.io/en/latest/userguide/development_mode.html).

It's also worth installing [Marksman LSP](https://github.com/artempyanykh/marksman) if you plan on working with plaintext files a lot. This should work with major CLI editors including Helix, Neovim, and Spacemacs, as well as KATE. I use Helix.

For viewing files as formatted you can use [MD Fileserver]( https://github.com/commenthol/md-fileserver ) with `mdstart`.

`diff` comes by default on the command line and can be extremely helpful when combining duplicate notes (which Obsidian's multiple vaults tend to lead to).

## Usage

ZenKat supports basic filtering, formatting, and sorting of results based on the fields it indexes. As of version v0.0.10 it indexes documents, links, and tags and can recursively access properties. You can customise the output using `--format`.

```
zenkat list pages --filter "tags.name has writing" --format "{rel_path} {tags.name}"
```

One of the most powerful features of ZenKat is the ability to calculate backlinks and resolve paths:
```
zenkat list pages --sort "in_link_count asc"
```

It can correctly operate over dates using filters.

```
zenkat list pages --filter "created_at > Sep 25 2023"
```

You can also combine multiple filters, which will act like an AND statement.

```
zenkat list pages --filter "rel_path has business" --filter "rel_path has Client"
```

You can sort by fields using straightforward ascending / descending statements. Note that you can only sort on one field at the moment.

```
zenkat list pages --filter "rel_path has business" --sort "modified_at asc" --format "{modified_at} {filename}"
```

You can get a simple list of tags and then find which pages have those tags:

```
zenkat list tags
zenkat list pages --filter "any tags.name = daily"
```

### Fields

#### Pages
```
title: str # filename without extensions
filename: str
abs_path: str
rel_path: str
created_at: datetime
modified_at: datetime
tags: list[Tag]
out_links: list[Link] # external links are not indexed for now
out_link_count: int
in_links: list[Link]
in_link_count: int
word_count: int
```

#### Tags

```
name: str
count: int
docs: str[str] # absolute paths of source documents
```

#### Links

```
text: str
href: str # the exact text of the link
href_resolved: str
doc_abs_path: str
type: str # wiki or regular
```

### Formatting

You can format the output of zenkat by using a format string in Python format. Note that this no longer uses `.format()` but instead uses regexps to support subfields.

```
zenkat list pages --format "[↓{in_link_count} ↑{out_link_count}] {title}, {word_count} words ({rel_path})"

zenkat list links --format "{doc_abs_path} → {href_resolved}"
```

As of v0.0.10 formatting can make use of subfields of pages correctly.

```
zenkat list pages --format "{title} {rel_path} {out_links.text} {in_links.doc_abs_path}"
```

### Filters

Currently filters use a basic token structure, separated by spaces. The last argument can be multiple words long. The format of filters is:

```
any tags.name = writing
[all | any] field[.subfield*] operation value
```

Subfields become lists which can be queried by using the `any` and `all` keywords. (Effectively, the `.` is a map command).

```
any tags.name = writing
```

As of v0.0.10 `dateutil` is used to parse dates, meaning most date strings will work as expected.

```
created_at < 2023-10
created_at > Jun 2023
created_at > September 10, 2023
```

Operations currently supported are:

```
=
>
<
>=
<=
has (opposite of in, works on sets, lists, strings, and dicts)
```

### Sorting

You can sort by any non-compound field using the following syntax.

```
<FIELD> {asc / desc}
modified_at asc
```