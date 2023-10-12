# Queries

From v0.1 zenkat supports queries in ZQL (Zen Query Language), a simple query language similar to SQL. For example:

```
list pages {lists.*.text}
where any lists.*.text has business
sort asc
```

There are two ways to use query syntax from the CLI. The first is directly with the -q flag:

```
zenkat query -q "list pages {lists.*.text} where any lists.*.text has business"
```

However this can be verbose, so the default behaviour is to load from config and use these as macros:

```
# in config.toml
[queries]
reduce_test = "list pages {lists.*.text} where any lists.*.text has business"

# on the command line
zenkat query reduce_test
```

The current syntax of the query language (not accounting for edge cases) is:

```
list COLLECTION [FORMAT]
[where [all | any] FIELD[.SUBFIELD*] OP EXPR]
[sort FIELD[.SUBFIELD*] ASC | DESC]
```
