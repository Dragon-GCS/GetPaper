import tkinter as tk
from tkinter.filedialog import asksaveasfilename, askdirectory
from tkinter.ttk import Frame, Combobox, Button, Scrollbar

from getpaper.utils import getTranslator, getTranslatorList
from getpaper.config import FRAME_STYLE, FONT


class DetailWindow(tk.Toplevel):
    def __init__(self, detail):
        super().__init__()
        self.title = "文章详情"
        self.option_add("*Font", FONT)
        self.columnconfigure(0, weight=1)   # 随宽度变化
        self.rowconfigure(1, weight=1)      # 随高度变化

        ################# 功能区 #################
        self.frame = Frame(self, **FRAME_STYLE)
        self.frame.columnconfigure(1, weight=1)
        self.frame.grid(sticky = tk.EW)
        
        Button(self.frame, text="下载", command=self.download).grid(row = 0)
        Button(self.frame, text="翻译", command=self.translate).grid(row = 0, column = 2, sticky=tk.E)
        # 选择翻译引擎
        self.choose = Combobox(self.frame, values=getTranslatorList(), state="readonly")
        self.choose.current(0)
        self.choose.grid(row = 0, column = 3, sticky=tk.W)
        self.choose.bind('<<ComboboxSelected>>', self.chooseTranslator)
        self.translator = getTranslator(self.choose.get())

        ################# 文章详情 #################
        self.detail_frame = Frame(self, **FRAME_STYLE)
        self.detail_frame.columnconfigure(0, weight = 1)
        self.detail_frame.rowconfigure(0, weight = 1)
        self.detail_frame.grid(row = 1, sticky=tk.NSEW)
        self.text = tk.Text(self.detail_frame, font=FONT)
        # https://tkdocs.com/shipman/text-index.html
        self.text.insert('insert', chars="\n".join(detail))
        self.text.grid(sticky=tk.NSEW)
        # 添加垂直滚动条
        vbar = Scrollbar(self.detail_frame, orient = 'vertical', command = self.text.yview)
        self.text.configure(yscrollcommand = vbar.set)
        vbar.grid(row = 0, column = 1, sticky = tk.NS)

    def chooseTranslator(self, event):
        self.translator = getTranslator(self.choose.get())
        self.choose.selection_clear()
        print("choose translator:", self.choose.get())

    def download(self) -> None:
        filename = asksaveasfilename(parent = self, defaultextension = ".pdf", filetypes=[("pdf", ".pdf")])
        print("Save file to file:", filename)
        self.text.insert("insert", "fhdisaofdsayiuogyuaiofdsahjkdlzhfudiaoyfdiua"*50)
        pass

    def translate(self):
        print("translate by :", self.translator)
        self.text.delete('1.0', "insert")
        self.text.insert("insert", "飞机都塞哥i哦萨芬v明年初卡西欧积分"*5)
        pass
        