import logging
import tkinter as tk
from tkinter.filedialog import asksaveasfilename
from tkinter.ttk import Button, Combobox, Frame, Scrollbar
from typing import Sequence

from getpaper.GUI.main_frame import TipFrame
from getpaper.config import FONT, FRAME_STYLE, RESULT_LIST_CN, RESULT_LIST_EN, translator_list
from getpaper.download import Downloader
from getpaper.utils import getTranslator, startThread

log = logging.getLogger("GetPaper")

class TextFrame(Frame):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.columnconfigure(0, weight = 1)
        self.rowconfigure(0, weight = 1)
        # Result display frame
        self.text = tk.Text(self, font = FONT, wrap = "word")
        self.text.grid(row = 0, column = 0, sticky = tk.NSEW)
        # Add vertical scroll bar
        vbar = Scrollbar(self, orient = "vertical", command = self.text.yview)
        self.text.configure(yscrollcommand = vbar.set)
        vbar.grid(row = 0, column = 1, sticky = tk.NS)

    def enShow(self, detail: Sequence[str]) -> None:
        """
        Show the infomation of paper with origin language on en_text_frame
        Args:
            detail: Paper's origin infomation, from search result
        """

        self._show(detail, RESULT_LIST_EN)

    def cnShow(self, detail: Sequence[str]) -> None:
        """
        Show the infomation of paper with Chinese on cn_text_frame
        Args:
            detail: Paper's infomation that title and abstract were tanslated.
        """

        self._show(detail, RESULT_LIST_CN)

    def _show(self, detail: Sequence[str], header: Sequence[str]) -> None:
        """
        Print the detail and corresponding header on the text frame
        Args:
            detail: Paper's detail infomation
                    Include title, authors, date, publication, abstract, doi, web_url.
            header: Headers corresponding to the detail
        """

        # https://tkdocs.com/shipman/text-index.html
        self.text.delete("1.0", "insert")
        for i, item in enumerate(header):
            self.text.insert("insert", item)
            self.text.insert("insert", f"{detail[i]}\n\n")


class DetailWindow(tk.Toplevel):
    def __init__(self, detail: Sequence[str], downloader: Downloader):
        super().__init__()
        self.title = "文章详情"
        self.option_add("*Font", FONT)
        self.columnconfigure(0, weight = 1) # Column 0 changes with window's weight
        self.rowconfigure(1, weight = 1)    # Row 1 changes with window's height
        self.geometry("1080x720")
        self.downloader = downloader
        self.detail = detail

        ################# Functional Frame #################
        self.frame = Frame(self, **FRAME_STYLE)
        for i in range(8):
            self.frame.columnconfigure(i + 1, weight = 1)
        self.frame.grid(sticky = tk.EW)
        # Download Button
        self.download_button = Button(self.frame, text = "下载", command = self.download)
        self.download_button.grid(row = 0)
        # Progress Bar
        self.tip = TipFrame(self.frame)
        # Translate Button
        self.trans_button = Button(self.frame, text = "翻译", command = self.translate)
        self.trans_button.grid(row = 0, column = 8, sticky = tk.E)
        # Choose the translator
        self.choose = Combobox(self.frame, values = translator_list, state = "readonly")
        self.choose.current(0)
        self.choose.grid(row = 0, column = 9, sticky = tk.W)
        self.choose.bind("<<ComboboxSelected>>", self.chooseTranslator)
        self.chooseTranslator()

        ################# Detail Text Frame #################
        self.detail_frame = Frame(self, **FRAME_STYLE)
        self.detail_frame.columnconfigure(0, weight = 1)
        self.detail_frame.columnconfigure(1, weight = 1)
        self.detail_frame.rowconfigure(0, weight = 1)
        self.detail_frame.grid(row = 1, sticky = tk.NSEW)
        # Origin language detail
        self.en_text = TextFrame(self.detail_frame)
        self.en_text.text.config(font = ("Times", 14))  # Set English font
        self.en_text.grid(row = 0, column = 0, sticky = tk.NSEW)
        self.en_text.enShow(self.detail)
        # Perform the translation result 
        self.ch_text = TextFrame(self.detail_frame)
        self.ch_text.grid(row = 0, column = 1, sticky = tk.NSEW)

    def chooseTranslator(self, event = None):
        """
        Choose a translator by ComboBox
        Args:
            event: Placeholder
        """

        self.translator = getTranslator(self.choose.get())
        self.choose.selection_clear()
        log.info(f"choose translator: {self.choose.get()}")

    @startThread("Download_Paper")
    def download(self) -> None:
        """Download this paper"""

        filename = asksaveasfilename(parent = self, 
                                     defaultextension = ".pdf", 
                                     filetypes = [("pdf", ".pdf")])

        if not filename:
            return

        self.download_button.state(["disabled"])
        self.tip.grid(row = 0, column = 5, columnspan = 3, sticky = tk.EW)
        self.tip.setTip("下载中...")
        try:
            self.downloader.download(self.detail[5], filename)
            self.tip.bar.stop()
        except Exception as e:
            log.error(f"Download Paper Error: {e}")
            self.tip.setTip("未知错误")
        else:
            self.tip.setTip("下载完成")
        finally:
            self.tip.bar.stop()
            self.download_button.state(["!disabled"])

    @startThread("Translate")
    def translate(self) -> None:
        """Translate this paper's title and abstract by selected translator"""

        log.info(f"translate by : {self.translator.__module__}",)
        self.trans_button.state(["disabled"])
        # Show TipBar
        self.tip.grid(row = 0, column = 5, columnspan = 3, sticky = tk.EW)
        self.tip.setTip("翻译中...")
        self.tip.bar.start()
        try:
            zh_detail = [item for item in self.detail]  # change tuple to list
            zh_detail[0] = self.translator.translate(self.detail[0])
            zh_detail[4] = self.translator.translate(self.detail[4])
            self.ch_text.cnShow(zh_detail)
        except Exception as e:
            self.ch_text.cnShow([str(e)])
        finally:
            self.tip.bar.stop()
            # Close TipBar
            self.tip.grid_remove()
            self.trans_button.state(["!disabled"])
