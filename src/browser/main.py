from .url import URL


def show(body: str, view_source: bool = False):
    if view_source:
        print(body)
        return

    in_tag = False
    entity = None

    entities = {
        "&lt;": "<",
        "&gt;": ">",
    }
    for c in body:
        if c == "<":
            in_tag = True
        elif c == ">":
            in_tag = False
        elif not in_tag:
            if c == "&":
                entity = c
            elif entity:
                entity += c
                if c == ";":
                    entity = entities.get(entity, entity)
                    print(entity, end="")
                    entity = None
            else:
                print(c, end="")


def load(url: URL):
    body = url.request()
    show(body, view_source=url.view_source)


def start():
    import sys

    load(URL(sys.argv[1]))
