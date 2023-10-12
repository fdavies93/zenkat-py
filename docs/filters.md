# Filters

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
~=
>
<
>=
<=
has (in with reversed direction, works on sets, lists, strings, and dicts)
~has (opposite of has)
```
