import logging
import tkinter
import tkinter.font
from tkinter import BOTH

from .css_parser import CSSParser, cascade_priority, style
from .layout import V_STEP
from .layout.document import DocumentLayout
from .parser import HTMLParser, Element, print_tree
from .url import URL

WIDTH, HEIGHT = 800, 600
SCROLL_STEP = 100

DEFAULT_STYLE_SHEET = CSSParser(open("browser.css").read()).parse()


def paint_tree(layout_object, display_list):
    display_list.extend(layout_object.paint())

    for child in layout_object.children:
        paint_tree(child, display_list)


def tree_to_list(tree, list):
    list.append(tree)
    for child in tree.children:
        tree_to_list(child, list)
    return list


class Browser:
    def __init__(self):
        self.scroll = 0
        self.width = WIDTH
        self.height = HEIGHT

        self.nodes = None
        self.document = None
        self.rules = None
        self.display_list = []

        self.window = tkinter.Tk()

        self.canvas = tkinter.Canvas(
            self.window, width=self.width, height=self.height, bg="white"
        )
        self.canvas.pack(fill=BOTH, expand=1)

        self.window.bind("<Down>", self.scroll_down)
        self.window.bind("<Up>", self.scroll_up)
        # TODO: Add support for <Mousewheel> on MacOS
        self.window.bind("<Button-4>", self.scroll_down)
        self.window.bind("<Button-5>", self.scroll_up)

        self.window.bind("<Control-d>", self.dump_dom)
        self.window.bind("<Control-l>", self.dump_layout_tree)
        self.window.bind("<Control-s>", self.dump_style_sheet)

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

        self.rules = DEFAULT_STYLE_SHEET.copy()

        links = [
            node.attributes["href"]
            for node in tree_to_list(self.nodes, [])
            if isinstance(node, Element)
            and node.tag == "link"
            and node.attributes.get("rel") == "stylesheet"
            and "href" in node.attributes
        ]
        for link in links:
            style_url = url.resolve(link)
            try:
                logging.debug(f"Loading stylesheet: {style_url}")
                style_sheet = style_url.request()
            except:
                logging.error(f"Failed to load stylesheet: {style_url}")
                continue
            self.rules.extend(CSSParser(style_sheet).parse())

        self.rules = sorted(self.rules, key=cascade_priority)

        style(self.nodes, self.rules)
        self.update()

    def update(self):
        self.document = DocumentLayout(self.nodes, self.width)
        self.document.layout()
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

    def scroll_down(self, _e):
        max_y = max(self.document.height + 2 * V_STEP - self.height, 0)
        self.scroll = min(self.scroll + SCROLL_STEP, max_y)
        self.draw()

    def scroll_up(self, _e):
        self.scroll = max(0, self.scroll - SCROLL_STEP)
        self.draw()

    def dump_dom(self, _e):
        print_tree(self.nodes)

    def dump_layout_tree(self, _e):
        print_tree(self.document)

    def dump_style_sheet(self, _e):
        for rule in self.rules:
            print(rule)
