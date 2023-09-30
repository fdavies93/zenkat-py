[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

# ZenKat

ZenKat is a tool and library to enable using a set of plaintext files, especially markdown files, as a [Zettelkasten](https://en.wikipedia.org/wiki/Zettelkasten) knowledge base.

I've used a number of knowledge management tools including Obsidian, Notion, and Coda, and have found them all lacking and / or designed in a way that makes them act as a walled garden. ZenKat is an attempt to create a lightweight FOSS alternative for command-line users.

It's named this way because of my bad memory for German. I remembered ZEttelKAsTen as ZenKat (unclear where the N came from).

## Recommended Setup

Zenkat has no dependencies beyond the Python standard library and can be [installed from PyPi](https://pypi.org/project/zenkat/).

```
pip install zenkat
```

It's also worth installing [Marksman LSP](https://github.com/artempyanykh/marksman) if you plan on working with plaintext files a lot. This should work with major CLI editors including Helix, Neovim, and Spacemacs, as well as KATE. I use Helix.

For viewing files as formatted you can use [MD Fileserver](https://github.com/commenthol/md-fileserver).

## Usage

ZenKat supports basic filtering, formatting, and sorting of results based on the fields it indexes. At the moment it can output pages and current tags used across pages. You can customise the output using `--format`. For example, with an alias of `zk`:

```
zk list --filter "tags has todo" --format "{rel_path} {tags}"
```

One of the most powerful features of ZenKat is the ability to calculate backlinks and resolve paths:
```
zk list --format "{title} [↓{in_link_count} ↑{out_link_count}] ({rel_path})" --sort "in_link_count asc"
```

It can correctly operate over dates using filters.

```
zk list --filter "created_at > Sep 25 2023 10:00AM"
```

You can also combine multiple filters, which will act like an AND statement.

```
zk list --filter "rel_path has business" --filter "rel_path has Client"
```

You can sort by fields using straightforward ascending / descending statements. Note that you can only sort on one field at the moment.

```
zk list --filter "rel_path has business" --sort "modified_at asc" --format "{modified_at} {filename}"
```

You can get a simple list of tags and then find which pages have those tags:

```
zk tags
zk list --filter "tags has personal"
```

### Fields

```
title: str
filename: str
abs_path: str
rel_path: str
created_at: datetime
modified_at: datetime
tags: set[str]
out_links: set[str]
out_link_count: int
in_links: set[str]
in_link_count: int
```

### Filters

Currently filters use a basic 3-token structure, separated by spaces. The last argument can be multiple words long. The format of filters is:

```
rel_path has college stuff
<FIELD> <OPERATION> <VALUE>
```

Operations currently supported are:

```
=
>
<
>=
<=
has (opposite of in, works on sets, strings, and dicts)
```

### Sorting

You can sort by any non-compound field using the following syntax:

```
<FIELD> {asc / desc}
modified_at asc
```