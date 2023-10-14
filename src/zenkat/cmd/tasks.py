from zenkat import index
import zenkat.filter
import zenkat.objects
from rich.console import Console

def tasks(args, console: Console, config: dict):
    idx = index.index(args.path, config)
    # the first filter applies to the tasks
    # the second filter applies to the page
    # all others are ignored
    filter_strs = []
    if args.filter != None:
        filter_strs = args.filter

    pages = idx.pages

    li_filter = None
    if len(filter_strs) > 0:
        li_filter = zenkat.filter.parse_filter(filter_strs[0], zenkat.objects.ListItem)
    if args.page != None:
        page_filter = zenkat.filter.parse_filter(args.page, zenkat.objects.Page)
        pages = list(filter(page_filter, pages))

    status_symbols = config["theme"]["tasks"]["symbols"]
    status_tags = config["theme"]["tasks"]["tags"]

    li_limit = 0
    if args.limit != None:
        li_limit = int(args.limit)
    
    li_no = 0

    # tasks should be a compound data structure or tuple
    # i.e. REQUIRES REWRITE TO BE MORE IDIOMATIC
    for p in pages:
        lis = []
        for ls in p.lists:
            l = ls
            if li_filter is not None: l = list(filter(li_filter, l))
            l = list(filter(lambda li: li.type == "task", l))
            lis = lis + l
        # now we have our list items filtered correctly
        if len(lis) > 0:
            console.print(f"[link]{p.title}[/link]")
        for li in lis:
            t1, t2 = "",""
            if li.status in status_tags:
                t1, t2 = status_tags[li.status]
            sym = status_symbols.get(li.status)
            console.print(f"[status]{sym}[/status] {t1}{li.text}{t2}")
            li_no += 1
            if li_limit != 0 and li_no > li_limit:
                return
