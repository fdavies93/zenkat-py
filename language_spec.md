Modelled after the DQL for Obsidian Dataframes, which uses a SQL-like syntax
[https://blacksmithgu.github.io/obsidian-dataview/queries/structure/]


```
LIST <data format / presentation>
FROM #poems <source>
WHERE  <filters>
```

For example:
```
LIST
FROM #assignments
WHERE status = "open"
```

If you also want to track tasks (i.e. content of files, not just metadata) might need to extend this syntax a bit.

Suitable method is probably to write a basic top-down parser.