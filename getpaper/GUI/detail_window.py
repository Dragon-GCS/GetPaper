import tkinter as tk
from tkinter.filedialog import asksaveasfilename
from tkinter.ttk import Button, Combobox, Frame, Scrollbar
from typing import List, Tuple, Union

from getpaper.GUI.main_frame import TipFrame
from getpaper.config import FONT, FRAME_STYLE, RESULT_LIST_CN, RESULT_LIST_EN, translator_list
from getpaper.download import Downloader
from getpaper.utils import getTranslator, startThread


class TextFrame(Frame):
    def __init__(self, master, detail: Union[List, Tuple] = (), **kwargs) -> None:
        super().__init__(master = master, **kwargs)
        self.columnconfigure(0, weight = 1)
        self.rowconfigure(0, weight = 1)
        # 结果显示区
        self.text = tk.Text(self, font = FONT)
        self.text.grid(row = 0, column = 0, sticky = tk.NSEW)
        # 添加垂直滚动条
        vbar = Scrollbar(self, orient = 'vertical', command = self.text.yview)
        self.text.configure(yscrollcommand = vbar.set)
        vbar.grid(row = 0, column = 1, sticky = tk.NS)

    def enShow(self, detail: Union[List, Tuple]) -> None:
        self._show(detail, RESULT_LIST_EN)

    def cnShow(self, detail: Union[List, Tuple]) -> None:
        self._show(detail, RESULT_LIST_CN)

    def _show(self, detail: Union[List, Tuple], header: List):
        """Output detail as format"""
        # https://tkdocs.com/shipman/text-index.html
        self.text.delete('1.0', "insert")
        for i, item in enumerate(header):
            self.text.insert("insert", item)
            self.text.insert("insert", detail[i] + "\n\n")


class DetailWindow(tk.Toplevel):
    def __init__(self, detail: Union[List[str], Tuple[str]], downloader: Downloader):
        super().__init__()
        self.title = "文章详情"
        self.option_add("*Font", FONT)
        self.columnconfigure(0, weight = 1)  # 随宽度变化
        self.rowconfigure(1, weight = 1)  # 随高度变化
        self.geometry("1080x720")
        self.downloader = downloader
        self.detail = detail

        ################# 功能区 #################
        self.frame = Frame(self, **FRAME_STYLE)
        for i in range(8):
            self.frame.columnconfigure(i + 1, weight = 1)
        self.frame.grid(sticky = tk.EW)
        # 下载按钮
        self.download_button = Button(self.frame, text = "下载", command = self.download)
        self.download_button.grid(row = 0)
        # 提示条
        self.tip = TipFrame(self.frame)
        # 翻译按钮
        self.trans_button = Button(self.frame, text = "翻译", command = self.translate)
        self.trans_button.grid(row = 0, column = 8, sticky = tk.E)
        # 选择翻译引擎
        self.choose = Combobox(self.frame, values = translator_list, state = "readonly")
        self.choose.current(0)
        self.choose.grid(row = 0, column = 9, sticky = tk.W)
        self.choose.bind('<<ComboboxSelected>>', self.chooseTranslator)
        self.chooseTranslator()

        ################# 文章详情 #################
        self.detail_frame = Frame(self, **FRAME_STYLE)
        self.detail_frame.columnconfigure(0, weight = 1)
        self.detail_frame.columnconfigure(1, weight = 1)
        self.detail_frame.rowconfigure(0, weight = 1)
        self.detail_frame.grid(row = 1, sticky = tk.NSEW)
        # 英文详情
        self.en_text = TextFrame(self.detail_frame, detail = self.detail)
        self.en_text.text.config(font = ("Times", 14))  # 设置英文字体
        self.en_text.grid(row = 0, column = 0, sticky = tk.NSEW)
        self.en_text.enShow(self.detail)
        # 翻译结果 
        self.ch_text = TextFrame(self.detail_frame, detail = self.detail)
        self.ch_text.grid(row = 0, column = 1, sticky = tk.NSEW)

    def chooseTranslator(self, event = None):
        self.translator = getTranslator(self.choose.get())
        self.choose.selection_clear()
        print("choose translator:", self.choose.get())

    def download(self) -> None:
        filename = asksaveasfilename(parent = self, defaultextension = ".pdf", filetypes = [("pdf", ".pdf")])
        print("Save file to file:", filename)
        self.en_text.enShow(["fhdisaofdsayiuogyuaiofdsahjkdlzhfudiaoyfdiua"] * 50)
        pass

    @startThread("Translate")
    def translate(self):
        print("translate by :", self.translator)
        self.trans_button.state(["disabled"])
        # 显示Tip bar
        self.tip.grid(row = 0, column = 5, columnspan = 3, sticky = tk.EW)
        self.tip.setTip("翻译中...")
        self.tip.bar.start()
        try:
            zh_detail = [item for item in self.detail]  # change tuple to list
            zh_detail[0] = self.translator.translate(self.detail[0])
            zh_detail[4] = self.translator.translate(self.detail[4])
            self.ch_text.cnShow(zh_detail)
        except Exception as e:
            self.ch_text.cnShow([e])
        finally:
            self.tip.bar.stop()
            # 关闭Tip bar
            self.tip.grid_remove()
            self.trans_button.state(["!disabled"])
