from zenkat.filter import parse_filter, filter_objs
from zenkat.sort import sort_from_query
from zenkat.objects import Index
from dataclasses import dataclass, field

@dataclass
class QueryData:
    results: list = field(default_factory=list)
    format_type: str = ""
    format_str: str = ""
    corpus: str = ""

def parse_query(query: str, index: Index) -> QueryData:
    clauses = {
        "format": [],
        "where": [],
        "sort": []
    }
    cur_clause = "format"
    acc = []
    # split into clauses
    words = query.split()
    for word in words:
        if word.lower() in clauses:
            clauses[cur_clause] = acc
            cur_clause = word.lower()
            acc = []
            continue
        acc.append(word)
    if len(acc) > 0: clauses[cur_clause] = acc

    output = QueryData()
    # get collection
    if len(clauses["format"]) < 2: raise ValueError("Format clause must have 2 or more arguments. e.g. list pages")
    output.format_type = clauses["format"][0]
    output.corpus = clauses["format"][1]
    data = index.__dict__.get(clauses["format"][1])
    if data == None: raise ValueError(f"No collection called {clauses[1]}!")
    if len(clauses["format"]) > 2: output.format_str = " ".join(clauses["format"][2:])
    # filter by objs
    if len(clauses["where"]) != 0 and len(data) > 0:
        if len(clauses["where"]) not in (3,4): raise ValueError("Filter clause must have 3-4 arguments. e.g. where rel_path has business")
        filter = parse_filter(" ".join(clauses["where"]), data[0])
        data = filter_objs(data, [filter])
    if len(clauses["sort"]) != 0:
        if len(clauses["sort"]) != 2: raise ValueError("Sort clause must have 2 arguments e.g. sort word_count asc")
        data = sort_from_query(data, " ".join(clauses["sort"]))

    output.results = data
    return output