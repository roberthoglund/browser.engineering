class Text:
    def __init__(self, text):
        self.text = text

    def __str__(self):
        return self.text


class Tag:
    def __init__(self, tag):
        self.tag = tag

    def __str__(self):
        return f"<{self.tag}>"


def lex(body: str, view_source: bool = False):
    if view_source:
        return [Text(body)]

    out = []
    buffer = ""
    in_tag = False
    entity = None

    entities = {
        "&lt;": "<",
        "&gt;": ">",
        "&quot;": '"',
        "&amp;": "&",
        "&ndash;": "–",
        "&copy;": "©",
        "&#39;": "'",
    }
    for c in body:
        if c == "<":
            in_tag = True
            if buffer:
                out.append(Text(buffer))
            buffer = ""
        elif c == ">":
            in_tag = False
            out.append(Tag(buffer))
            buffer = ""
        else:
            if c == "&":
                entity = c
            elif entity:
                entity += c
                if c == ";":
                    mapped_entity = entities.get(entity, entity)
                    if mapped_entity == entity:
                        print(f"Unknown entity {entity}")
                    buffer += mapped_entity
                    entity = None
            else:
                buffer += c
    if not in_tag and buffer:
        out.append(Text(buffer))
    return out
