from browser.cmds import DrawRect, DrawText
from browser.layout.font_cache import get_font
from browser.parser import Element, Text

BLOCK_ELEMENTS = [
    "html",
    "body",
    "article",
    "section",
    "nav",
    "aside",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "hgroup",
    "header",
    "footer",
    "address",
    "p",
    "hr",
    "pre",
    "blockquote",
    "ol",
    "ul",
    "menu",
    "li",
    "dl",
    "dt",
    "dd",
    "figure",
    "figcaption",
    "main",
    "div",
    "table",
    "form",
    "fieldset",
    "legend",
    "details",
    "summary",
]


class BlockLayout:
    def __init__(self, node, parent, previous):
        self.node = node
        self.parent = parent
        self.previous = previous
        self.display_list = []
        self.children = []
        self.cursor_x = 0
        self.cursor_y = 0
        self.size = 12
        self.line = []
        self.center = False
        self.x = None
        self.y = None
        self.width = None
        self.height = None

    def __repr__(self):
        return "BlockLayout[{}](x={}, y={}, width={}, height={}, node={})".format(
            self.layout_mode(), self.x, self.y, self.width, self.height, self.node
        )

    def paint(self):
        cmds = []
        if isinstance(self.node, Element):
            if self.node.tag == "nav" and self.node.get_attribute("class") == "links":
                x2, y2 = self.x + self.width, self.y + self.height
                rect = DrawRect(self.x, self.y, x2, y2, "lightgray")
                cmds.append(rect)

            bg_color = self.node.style.get("background-color", "transparent")
            if bg_color != "transparent":
                x2, y2 = self.x + self.width, self.y + self.height
                rect = DrawRect(self.x, self.y, x2, y2, bg_color)
                cmds.append(rect)

        if self.layout_mode() == "inline":
            for x, y, word, font, color in self.display_list:
                cmds.append(DrawText(x, y, word, font, color))
        return cmds

    def layout_mode(self):
        if isinstance(self.node, Text):
            return "inline"
        elif any(
            [
                isinstance(child, Element) and child.tag in BLOCK_ELEMENTS
                for child in self.node.children
            ]
        ):
            return "block"
        elif self.node.children:
            return "inline"
        else:
            return "block"

    def layout(self):
        if self.previous:
            self.y = self.previous.y + self.previous.height
        else:
            self.y = self.parent.y

        self.x = self.parent.x
        self.width = self.parent.width

        mode = self.layout_mode()
        if mode == "block":
            previous = None
            for child in self.node.children:
                if isinstance(child, Element) and child.tag == "head":
                    continue
                next_node = BlockLayout(child, self, previous)
                self.children.append(next_node)
                previous = next_node
        else:
            self.cursor_x = 0
            self.cursor_y = 0
            self.size = 12

            self.line = []
            self.recurse(self.node)
            self.flush()

        for child in self.children:
            child.layout()

        if mode == "block":
            self.height = sum([child.height for child in self.children])
        else:
            self.height = self.cursor_y

    def recurse(self, node):
        if isinstance(node, Text):
            for word in node.text.split():
                self.word(node, word)
        else:
            if node.tag == "br":
                self.flush()
            for child in node.children:
                self.recurse(child)

    def word(self, node, word):
        weight = node.style["font-weight"]
        style = node.style["font-style"]
        if style == "normal":
            style = "roman"
        size = int(float(node.style["font-size"][:-2]) * 0.75)
        font = get_font(size, weight, style)

        color = node.style["color"]

        w = font.measure(word)
        if self.cursor_x + w > self.width:
            # Simple handling of soft hyphens.
            if "\u00AD" in word:
                word_tokens = word.split("\u00AD")
                split_pos = -1
                for i in range(len(word_tokens)):
                    broken_word = "\u00AD".join(word_tokens[:i]) + "\u00AD"
                    broken_word_w = font.measure(broken_word)
                    if self.cursor_x + broken_word_w > self.width:
                        split_pos = i - 1
                        break

                if split_pos > -1:
                    self.word("\u00AD".join(word_tokens[:split_pos]) + "\u00AD")
                    self.flush()
                    self.word("\u00AD".join(word_tokens[split_pos:]))
                    return

            self.flush()
        self.line.append((self.cursor_x, word, font, color, w))
        self.cursor_x += w + font.measure(" ")

    def flush(self):
        if not self.line:
            return

        metrics = [font.metrics() for x, word, font, col, w in self.line]
        max_ascent = max([metric["ascent"] for metric in metrics])
        baseline = self.cursor_y + 1.25 + max_ascent

        if self.center:
            min_x = min([x for x, word, font, col, w in self.line])
            max_x = max([x + w for x, word, font, col, w in self.line])
            left_offset = (self.width - (max_x - min_x)) // 2
            for i in range(len(self.line)):
                x, word, font, col, w = self.line[i]
                self.line[i] = (self.x + x + left_offset, word, font, col, w)

        for rel_x, word, font, col, w in self.line:
            x = self.x + rel_x
            y = self.y + baseline - font.metrics("ascent")
            self.display_list.append((x, y, word, font, col))

        max_descent = max([metric["descent"] for metric in metrics])
        self.cursor_y = baseline + 1.25 * max_descent

        self.cursor_x = 0
        self.line = []
