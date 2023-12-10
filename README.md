[![License: GPL
v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
![PyPI - Downloads](https://img.shields.io/pypi/dm/zenkat)

# ZenKat

## (2023-12-10) Development Note

I've been working on a major update (i.e. v0.2) on and off for the last couple
of months. You can see the progress I made on this on the feature/parsing branch
which includes many improvements to grouping, sorting, and config abilities,
along with the overall data model. However, due to some issues which are partly
the fault of my code and partly limitations in the libraries used, maintaining
the current version of the project has become exceptionally frustrating.

I've also been using nvim heavily recently and in the context of editor plugins,
Python has issues due to its module system. Since I'd ultimately like zenkat to
work with as many editors as possible and on the command-line, I've decided to
rewrite the core functionality in a compiled language. Rather than a v0.2
release it'll be a rewrite. Updates on this coming soon. 

If anyone is interested in maintaining the *Python version* of this project,
please file an issue asking to take over the repo and we can chat about it. 

## Foreword

ZenKat is a tool and library to enable using a set of plaintext files,
especially markdown files, as a
[Zettelkasten](https://en.wikipedia.org/wiki/Zettelkasten) knowledge base.

I've used a number of knowledge management tools including Obsidian, Notion, and
Coda, and have found them all lacking and / or designed in a way that makes them
act as a walled garden. ZenKat is an attempt to create a lightweight FOSS
alternative for command-line users. As such it aims to have few dependencies
while still providing decent features.

It's named this way because of my bad memory for German. I remembered
ZEttelKAsTen as ZenKat (unclear where the N came from).

![](images/zk-0-1.gif)

## Recommended Setup

You can install directly from pip:

``` pip install zenkat ```

This also installs the `zenkat` convenience script.

To configure themes and create custom queries and formats, make a file at
`~/.config/zenkat/config.toml`.

If you'd like to run directly from source you can clone the repository and use
[development
mode](https://setuptools.pypa.io/en/latest/userguide/development_mode.html).

It's also worth installing [Marksman
LSP](https://github.com/artempyanykh/marksman) if you plan on working with
plaintext files a lot. This should work with major CLI editors including Helix,
Neovim, and Spacemacs, as well as KATE. I use Helix.

For viewing files as formatted you can use [MD Fileserver](
https://github.com/commenthol/md-fileserver ) with `mdstart`.

`diff` comes by default on the command line and can be extremely helpful when
combining duplicate notes (which Obsidian's multiple vaults tend to lead to).

## Features

- Filter and sort through notes with powerful mapping syntax
- Customisable output formats and color schemes
- Supports markdown tags, and unpacks nested tags
- Resolves internal links, both inbound and outbound
- Loads YAML metadata headers in pages
- Task tracking with beautiful formatting, filters, and extended syntax
- Configuration using `config.toml` in your home folder: see
  [default_config](./src/zenkat/default_config.py) for options 

## Contents

- [Usage](./docs/usage.md)
- [Fields and Subfields](./docs/fields.md)
- [Formatting](./docs/formatting.md)
- [Filters](./docs/filters.md)
- [Sorting](./docs/sort.md)
- [Tasks](./docs/tasks.md)
- [grep and cat](./docs/grep.md)
- [Queries](./docs/queries.md)
- [Macros](./docs/macros.md)
