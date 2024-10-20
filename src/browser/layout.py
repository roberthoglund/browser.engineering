import tkinter

from browser.parser import Text

H_STEP, V_STEP = 13, 18

FONTS = {}


def get_font(size, weight, style):
    key = (size, weight, style)
    if key not in FONTS:
        font = tkinter.font.Font(size=size, weight=weight, slant=style)
        label = tkinter.Label(font=font)
        FONTS[key] = (font, label)
    return FONTS[key][0]


class Layout:
    def __init__(self, tree, width: int):
        self.display_list = []
        self.line = []
        self.cursor_x = H_STEP
        self.cursor_y = V_STEP
        self.weight = "normal"
        self.style = "roman"
        self.size = 12
        self.width = width
        self.center = False

        self.recurse(tree)
        self.flush()

    def recurse(self, tree):
        if isinstance(tree, Text):
            for word in tree.text.split():
                self.word(word)
        else:
            self.open_tag(tree)
            for child in tree.children:
                self.recurse(child)
            self.close(tree)

    def open_tag(self, tag):
        tag, attr = tag.tag, tag.attributes
        if tag == "i":
            self.style = "italic"
        elif tag == "b":
            self.weight = "bold"
        elif tag == "small":
            self.size -= 2
        elif tag == "big":
            self.size += 4
            self.cursor_y += V_STEP
        elif tag == "br":
            self.flush()
        elif tag.startswith("h1"):
            self.flush()
            if "class" in attr:
                self.center = "title" == attr["class"]
            self.size += 8

    def close(self, tag):
        tag, attr = tag.tag, tag.attributes
        if tag == "i":
            self.style = "roman"
        elif tag == "b":
            self.weight = "normal"
        elif tag == "small":
            self.size += 2
        elif tag == "big":
            self.size -= 4
        elif tag == "p":
            self.flush()
            self.cursor_y += V_STEP
        elif tag == "h1":
            self.size -= 8
            self.flush()
            self.center = False
        pass

    def word(self, word):
        font = get_font(self.size, self.weight, self.style)
        w = font.measure(word)
        if self.cursor_x + w > self.width - H_STEP:
            # Simple handling of soft hyphens.
            if "\u00AD" in word:
                word_tokens = word.split("\u00AD")
                split_pos = -1
                for i in range(len(word_tokens)):
                    broken_word = "\u00AD".join(word_tokens[:i]) + "\u00AD"
                    broken_word_w = font.measure(broken_word)
                    if self.cursor_x + broken_word_w > self.width - H_STEP:
                        split_pos = i - 1
                        break

                if split_pos > -1:
                    self.word("\u00AD".join(word_tokens[:split_pos]) + "\u00AD")
                    self.flush()
                    self.word("\u00AD".join(word_tokens[split_pos:]))
                    return

            self.flush()
        self.line.append((self.cursor_x, word, font, w))
        self.cursor_x += w + font.measure(" ")

    def flush(self):
        if not self.line:
            return

        metrics = [font.metrics() for x, word, font, w in self.line]
        max_ascent = max([metric["ascent"] for metric in metrics])
        baseline = self.cursor_y + 1.25 + max_ascent

        if self.center:
            min_x = min([x for x, word, font, w in self.line])
            max_x = max([x + w for x, word, font, w in self.line])
            left_offset = (self.width - (max_x - min_x)) // 2
            for i in range(len(self.line)):
                x, word, font, w = self.line[i]
                self.line[i] = (x + left_offset, word, font, w)

        for x, word, font, w in self.line:
            y = baseline - font.metrics("ascent")
            self.display_list.append((x, y, word, font))

        max_descent = max([metric["descent"] for metric in metrics])
        self.cursor_y = baseline + 1.25 * max_descent

        self.cursor_x = H_STEP
        self.line = []
