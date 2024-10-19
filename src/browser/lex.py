def lex(body: str, view_source: bool = False):
    if view_source:
        return body

    text = ""
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
                    text += entity
                    entity = None
            else:
                text += c

    return text
