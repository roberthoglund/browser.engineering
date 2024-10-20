import tkinter
import tkinter.font
from tkinter import BOTH

from .layout import Layout, V_STEP
from .parser import HTMLParser, print_tree
from .url import URL

WIDTH, HEIGHT = 800, 600
SCROLL_STEP = 100


class Browser:
    def __init__(self):
        self.scroll = 0
        self.width = WIDTH
        self.height = HEIGHT

        self.nodes = None
        self.display_list = []

        self.window = tkinter.Tk()

        self.canvas = tkinter.Canvas(self.window, width=self.width, height=self.height)
        self.canvas.pack(fill=BOTH, expand=1)

        self.window.bind("<Down>", self.scrolldown)
        self.window.bind("<Up>", self.scrollup)
        # TODO: Add support for <Mousewheel> on MacOS
        self.window.bind("<Button-4>", self.scrolldown)
        self.window.bind("<Button-5>", self.scrollup)

        self.window.bind("<Configure>", self.configure)

    def configure(self, e):
        if e.width != self.width or e.height != self.height:
            self.width = e.width
            if self.width < WIDTH:
                self.width = WIDTH
            self.height = e.height
            if self.height < HEIGHT:
                self.height = HEIGHT
            self.update()

    def load(self, url: URL):
        body = url.request()
        self.nodes = HTMLParser(body).parse()
        self.update()

    def update(self):
        self.display_list = Layout(self.nodes, self.width).display_list
        self.draw()

    def draw(self):
        self.canvas.delete("all")
        for x, y, word, font in self.display_list:
            if y > self.scroll + self.height:
                continue
            if y + V_STEP < self.scroll:
                continue
            self.canvas.create_text(
                x, y - self.scroll, text=word, font=font, anchor="nw"
            )

    def scrolldown(self, e):
        self.scroll += SCROLL_STEP
        self.draw()

    def scrollup(self, e):
        self.scroll -= SCROLL_STEP
        if self.scroll < 0:
            self.scroll = 0
        self.draw()
