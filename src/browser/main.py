import tkinter
from .browser import Browser
from .url import URL




def start():
    import sys

    Browser().load(URL(sys.argv[1]))
    tkinter.mainloop()
