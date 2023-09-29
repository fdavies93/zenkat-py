*Note that this project is in a very early stage right now.*

# ZenKat

ZenKat is a tool and library to enable using a set of plaintext files, especially markdown files, as a [Zettelkasten](https://en.wikipedia.org/wiki/Zettelkasten) knowledge base.

I've used a number of knowledge management tools including Obsidian, Notion, and Coda, and have found them all lacking and / or designed in a way that makes them act as a walled garden. ZenKat is an attempt to create a lightweight FOSS alternative for command-line users.

It's named this way because of my bad memory for German. I remembered ZEttelKAsTen as ZenKat (unclear where the N came from).

## Recommended Setup

ZenKat has no dependencies but also no easy install method. For now I recommend cloning the repo and creating an alias for `python3 zk.py` as `zk`.

It's also worth installing [Marksman LSP](https://github.com/artempyanykh/marksman) if you plan on working with plaintext files a lot. This should work with major CLI editors including Helix and Neovim. I use Helix.