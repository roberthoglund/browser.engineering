def print_tree(node, indent=0):
    print("  " * indent, node)
    for child in node.children:
        print_tree(child, indent + 2)


SELF_CLOSING_TAGS = [
    "area",
    "base",
    "br",
    "col",
    "embed",
    "hr",
    "img",
    "input",
    "link",
    "meta",
    "param",
    "source",
    "track",
    "wbr",
]


class Text:
    def __init__(self, text, parent):
        self.text = text
        self.children = []
        self.parent = parent

    def __repr__(self):
        return repr(self.text)


class Element:
    def __init__(self, tag, attributes, parent):
        self.tag = tag
        self.attributes = attributes
        self.children = []
        self.parent = parent

    def __repr__(self):
        if self.attributes:
            return f"<{self.tag} {self.attributes}>"
        return f"<{self.tag}>"


class HTMLParser:
    HEAD_TAGS = [
        "base",
        "basefont",
        "bgsound",
        "noscript",
        "link",
        "meta",
        "title",
        "style",
        "script",
    ]

    def __init__(self, body):
        self.body = body
        self.unfinished = []

    def parse(self):
        text = ""
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
        for c in self.body:
            if c == "<":
                in_tag = True
                if text:
                    self.add_text(text)
                text = ""
            elif c == ">":
                in_tag = False
                self.add_tag(text)
                text = ""
            else:
                if c == "&" and not in_tag:
                    entity = c
                elif entity:
                    entity += c
                    if c == ";":
                        mapped_entity = entities.get(entity, entity)
                        if mapped_entity == entity:
                            print(f"Unknown entity {entity}")
                        text += mapped_entity
                        entity = None
                else:
                    text += c
        if not in_tag and text:
            self.add_text(text)

        return self.finish()

    def add_text(self, text):
        if text.isspace():
            return
        self.implicit_tags(None)
        parent = self.unfinished[-1]
        node = Text(text, parent)
        parent.children.append(node)

    def add_tag(self, tag):
        tag, attributes = self.get_attributes(tag)
        if tag.startswith("!"):
            return
        self.implicit_tags(tag)
        if tag.startswith("/"):
            if len(self.unfinished) == 1:
                return
            node = self.unfinished.pop()
            parent = self.unfinished[-1]
            parent.children.append(node)
        elif tag in SELF_CLOSING_TAGS:
            parent = self.unfinished[-1]
            node = Element(tag, attributes, parent)
            parent.children.append(node)
        else:
            parent = self.unfinished[-1] if self.unfinished else None
            node = Element(tag, attributes, parent)
            self.unfinished.append(node)

    def implicit_tags(self, tag):
        while True:
            open_tags = [node.tag for node in self.unfinished]
            if open_tags == [] and tag != "html":
                self.add_tag("html")
            elif open_tags == ["html"] and tag not in ["head", "body", "/html"]:
                if tag in self.HEAD_TAGS:
                    self.add_tag("head")
                else:
                    self.add_tag("body")
            elif (
                open_tags == ["html", "head"] and tag not in ["/head"] + self.HEAD_TAGS
            ):
                self.add_tag("/head")
            elif len(open_tags) > 1 and open_tags[-1] == "p" and tag in ["p"]:
                self.add_tag("/p")
            else:
                break

    def finish(self):
        if not self.unfinished:
            self.implicit_tags(None)
        while len(self.unfinished) > 1:
            node = self.unfinished.pop()
            parent = self.unfinished[-1]
            parent.children.append(node)
        return self.unfinished.pop()

    def get_attributes(self, text):
        if text.endswith("/"):
            text = text[:-1]
        if " " not in text:
            return text, {}

        tag, rest = text.split(" ", 1)
        tag = tag.casefold()
        self.attribute_lexer(rest)
        attributes = self.attribute_lexer(rest)
        return tag, attributes

    def attribute_lexer(self, text):
        value = ""
        key = ""
        in_string = False
        in_value = False
        attributes = {}
        for c in text:
            if c == '"':
                in_string = not in_string
            elif c == "=" and not in_string:
                in_value = True
            elif c.isspace() and not in_string:
                if key:
                    attributes[key.casefold()] = value
                    key = None
                    value = ""
            elif in_value:
                value += c
            else:
                key += c

        if key:
            attributes[key.casefold()] = value

        return attributes
