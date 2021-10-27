import tkinter as tk
from tkinter import ttk
from tkinter.filedialog import askdirectory, asksaveasfilename

from ttkbootstrap import Style

from getpaper.GUI.main_frame import MainFrame
from getpaper.GUI.result_frame import ResultFrame
from getpaper.config import APP_NAME, FONT, FRAME_STYLE


class Application(Style):
    def __init__(self, theme):
        super().__init__(theme)
        self.master.title(APP_NAME)
        self.master.minsize(960, 600)
        self.master.geometry("1080x720")
        self.master.option_add("*Font", FONT)
        self.master.columnconfigure(0, weight = 1)  # 第一列随宽度变化
        self.master.rowconfigure(1, weight = 1)  # 第二行随高度变化

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

    def run(self):
        self.master.mainloop()

    def saveToFile(self):
        filename = asksaveasfilename(defaultextension = '.xslx', filetypes = [('xlsx', '.xlsx')])
        print("Save file to file:", filename)
        self.main_frame.saveToFile(filename)

    def downloadAll(self):
        dir = askdirectory()
        print("DownLoad All to dictory", dir)
        self.main_frame.downloadAll(dir)
