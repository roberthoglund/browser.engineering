import tkinter
from tkinter import BOTH

from .layout import layout
from .lex import lex
from .url import URL

WIDTH, HEIGHT = 800, 600
H_STEP, V_STEP = 13, 18
SCROLL_STEP = 100


class Browser:
    def __init__(self):
        self.scroll = 0
        self.width = WIDTH
        self.height = HEIGHT

        self.text = None
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
        self.text = lex(body, url.view_source)
        self.update()

    def update(self):
        self.display_list = layout(
            self.text, h_step=H_STEP, v_step=V_STEP, width=self.width
        )
        self.draw()

    def draw(self):
        self.canvas.delete("all")
        for x, y, c in self.display_list:
            if y > self.scroll + self.height:
                continue
            if y + V_STEP < self.scroll:
                continue
            self.canvas.create_text(x, y - self.scroll, text=c)

    def scrolldown(self, e):
        self.scroll += SCROLL_STEP
        self.draw()

    def scrollup(self, e):
        self.scroll -= SCROLL_STEP
        if self.scroll < 0:
            self.scroll = 0
        self.draw()
