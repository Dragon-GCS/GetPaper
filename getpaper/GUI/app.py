import logging
import os
import tkinter as tk
from tkinter import ttk
from tkinter.filedialog import askdirectory, asksaveasfilename

from ttkbootstrap import Style

from getpaper.GUI.main_frame import MainFrame
from getpaper.GUI.menu import MenuBar
from getpaper.GUI.result_frame import ResultFrame
from getpaper.config import APP_NAME, FONT, FRAME_STYLE

log = logging.getLogger("GetPaper")

class Application(Style):
    def __init__(self, theme: str) -> None:
        super().__init__(theme)
        self.master.title(APP_NAME)
        self.master.minsize(960, 600)               # Minimun window size
        self.master.geometry("1080x720")            # Default window size
        self.master.option_add("*Font", FONT)       # Set font
        # Column 1st (main_frame & result_frame)changes with main window's weight
        self.master.columnconfigure(0, weight = 1)
        # Row 2nd (result_frame) changes with main window's height
        self.master.rowconfigure(1, weight = 1)

        self.result_frame = ResultFrame(self.master, relief = FRAME_STYLE["relief"])
        self.main_frame = MainFrame(self.master, self.result_frame, **FRAME_STYLE)

        style = ttk.Style()
        style.configure("TButton", font = FONT)
        style.configure("Treeview", font = ("times", 12))
        style.configure("Heading", font = FONT)

        menu = MenuBar(self)
        self.master["menu"] = menu

    def run(self) -> None:
        """Run the App"""
        self.master.mainloop()
