import logging
import os
import tkinter as tk
from tkinter import ttk
from tkinter.filedialog import askdirectory, asksaveasfilename

from ttkbootstrap import Style

from getpaper.GUI.main_frame import MainFrame
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
        style.configure('TButton', font = FONT)
        style.configure('Treeview', font = ("times", 12))
        style.configure('Heading', font = FONT)

        menu = tk.Menu(self.master)
        menu.add_command(label = '数据导出', command = self.saveToFile)
        menu.add_command(label = '全部下载', command = self.downloadAll)
        self.master['menu'] = menu

    def run(self) -> None:
        """Run the App"""
        self.master.mainloop()

    def saveToFile(self) -> None:
        """Save search result to csv file"""

        if not hasattr(self.main_frame, "result"):
            self.main_frame.tip.setTip("无搜索结果")
        else:
            filename = asksaveasfilename(defaultextension = '.csv', filetypes = [('csv', '.csv')])
            if filename:
                filename = os.path.abspath(filename)
                log.info(f"Save file to file: {filename}")
                self.main_frame.saveToFile(filename)

    def downloadAll(self) -> None:
        """Download PDFs of all results to specified directory"""

        if not hasattr(self.main_frame, "result"):
            self.main_frame.tip.setTip("无搜索结果")
        else:
            target_dir = askdirectory()
            if target_dir:
                target_dir = os.path.abspath(target_dir)
                log.info(f"Downloading all paper to dictory: {target_dir}")
                self.main_frame.downloadAll(target_dir)
