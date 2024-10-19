import importlib.metadata
import tkinter
from .browser import Browser
from .url import URL


def get_version():
    version = importlib.metadata.version("browser.engineering")
    parts = version.split(".")
    while parts and parts[-1] == "0":
        parts.pop()
    return ".".join(parts)


def start():
    import sys

    Browser().load(URL(sys.argv[1], version=get_version()))
    tkinter.mainloop()


if __name__ == "__main__":
    start()
