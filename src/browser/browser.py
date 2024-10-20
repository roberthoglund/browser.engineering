import tkinter
import tkinter.font
from tkinter import BOTH

from .layout import DocumentLayout, V_STEP
from .parser import HTMLParser, print_tree
from .url import URL

WIDTH, HEIGHT = 800, 600
SCROLL_STEP = 100


def paint_tree(layout_object, display_list):
    display_list.extend(layout_object.paint())

    for child in layout_object.children:
        paint_tree(child, display_list)


class Browser:
    def __init__(self):
        self.scroll = 0
        self.width = WIDTH
        self.height = HEIGHT

        self.nodes = None
        self.document = None
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
        self.document = DocumentLayout(self.nodes, self.width)
        self.document.layout()
        print_tree(self.document)
        self.display_list = []
        paint_tree(self.document, self.display_list)
        self.draw()

    def draw(self):
        self.canvas.delete("all")
        for cmd in self.display_list:
            if cmd.top > self.scroll + self.height:
                continue
            if cmd.bottom < self.scroll:
                continue
            cmd.execute(self.scroll, self.canvas)

    def scrolldown(self, e):
        max_y = max(self.document.height + 2 * V_STEP - self.height, 0)
        self.scroll = min(self.scroll + SCROLL_STEP, max_y)
        self.draw()

    def scrollup(self, e):
        self.scroll = max(0, self.scroll - SCROLL_STEP)
        self.draw()
