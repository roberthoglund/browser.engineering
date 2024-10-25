import importlib.metadata
import tkinter
import logging

from .browser import Browser
from .url import URL

logging.basicConfig(
    level=logging.DEBUG,
    format="{asctime} - {levelname} - {message}",
    style="{",
    datefmt="%Y-%m-%d %H:%M:%S",
)


def get_version():
    version = importlib.metadata.version("browser.engineering")
    parts = version.split(".")
    while parts and parts[-1] == "0":
        parts.pop()
    return ".".join(parts)


def start():
    import sys

    url = URL(sys.argv[1], version=get_version())
    logging.info(f"Starting browser with URL: {url}")

    Browser().load(url)
    tkinter.mainloop()


if __name__ == "__main__":
    start()
