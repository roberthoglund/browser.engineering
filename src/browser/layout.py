import tkinter
from shutil import which

from browser.lex import Text

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
    def __init__(self, tokens, width: int):
        self.display_list = []
        self.line = []
        self.cursor_x = H_STEP
        self.cursor_y = V_STEP
        self.weight = "normal"
        self.style = "roman"
        self.size = 12
        self.width = width
        self.center = False

        for tok in tokens:
            self.token(tok)
        self.flush()

    def token(self, tok):
        if isinstance(tok, Text):
            for word in tok.text.split():
                self.word(word)
        elif tok.tag == "i":
            self.style = "italic"
        elif tok.tag == "/i":
            self.style = "roman"
        elif tok.tag == "b":
            self.weight = "bold"
        elif tok.tag == "/b":
            self.weight = "normal"
        elif tok.tag == "small":
            self.size -= 2
        elif tok.tag == "/small":
            self.size += 2
        elif tok.tag == "big":
            self.size += 4
        elif tok.tag == "/big":
            self.size -= 4
        elif tok.tag == "/p":
            self.flush()
            self.cursor_y += V_STEP
        elif tok.tag == "br":
            self.flush()
        elif tok.tag.startswith("h1"):
            self.flush()
            if 'class="title"' in tok.tag:
                self.center = True
            self.size += 8
        elif tok.tag == "/h1":
            self.size -= 8
            self.flush()
            self.center = False

    def word(self, word):
        font = get_font(self.size, self.weight, self.style)
        w = font.measure(word)
        if self.cursor_x + w > self.width - H_STEP:
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
