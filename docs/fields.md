# Fields and Subfields

Most properties (in dicts / objects) can be queried using normal field syntax. For lists of dictionaries or objects, this will map the property of the list items to the parent list.
```
metadata.name # return a string
tags.name # return a list of tag names
```

Specific list items can also be accessed using their index.
```
tags.0
```

For dealing with nested arrays you can use the * (reduce) operator:

```
lists.*.text
```

## Pages
```python
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
metadata: dict
headings: list[Heading]
outline: str
lists: list[list[ListItem]]
```

## Headings

```python
text: str
depth: int
children: list # not in use
```

## Tags

```python
name: str
count: int
docs: str[str] # absolute paths of source documents
```

## ListItem

```python
text: str
depth: int # indent level
type: str
status: Union[str,None]
children: list # not used
doc_abs_path: str
```

## Links

```python
text: str
href: str # the exact text of the link
href_resolved: str
doc_title: str
doc_abs_path: str
type: str # wiki or regular
```
