import tkinter as tk
from tkinter.ttk import Frame, Scrollbar, Treeview
from typing import Sequence

from getpaper.GUI.detail_window import DetailWindow
from getpaper.download import SciHubDownloader


class ResultFrame(Frame):
    def __init__(self, master: tk.Widget, **kwargs) -> None:
        super().__init__(master, **kwargs)
        self.grid(row = 1, sticky = tk.NSEW)
        self.columnconfigure(0, weight = 1)
        self.rowconfigure(0, weight = 1)

        # Set headers
        self.headers = ('标题', '作者', '发表时间', '期刊')
        self.tree = Treeview(self,
                             columns = self.headers,
                             show = 'headings')  # 不写show="headings"会空一列
        for head in self.headers:
            self.tree.column(head, anchor = "center")
            self.tree.heading(head, text = head)
        self.tree.grid(row = 0, sticky = tk.NSEW)

        # Add vertical scroll bar
        vbar = Scrollbar(self, orient = 'vertical', command = self.tree.yview)
        self.tree.configure(yscrollcommand = vbar.set)
        vbar.grid(row = 0, column = 1, sticky = tk.NS)

        # Display detail window by double click
        self.tree.bind('<Double-Button-1>', lambda e: self.showItem())

    def createForm(self, data: Sequence[Sequence[str]]) -> None:
        """
        Display search result on the result form.
        Args:
            data: Result sequence, each item's format is
                  (index, (title, authors, date, publication, abstract, doi, web))
        """

        # remove previous result
        for item in self.tree.get_children():
            self.tree.delete(item)
        # insert results
        for i, item in enumerate(data):
            self.tree.insert("", i, values = item)

    def showItem(self) -> None:
        """The binding function of double click, display detail window."""

        detail = self.tree.item(self.tree.selection()[0], "values")
        sci_url = self.master.children["!mainframe"].scihub_url.get()
        downloader = SciHubDownloader(sci_url)
        DetailWindow(detail, downloader)
