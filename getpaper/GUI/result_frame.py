import tkinter as tk
from tkinter.ttk import Frame, Scrollbar, Treeview
from typing import List

from getpaper.GUI.detail_window import DetailWindow


class ResultFrame(Frame):
    def __init__(self, master, **kwargs) -> None:
        super().__init__(master, **kwargs)
        self.grid(row = 1, sticky = tk.NSEW)
        self.columnconfigure(0, weight = 1)
        self.rowconfigure(0, weight = 1)

        # 设置表头
        self.headers = ('标题', '作者', '发表时间', '期刊')
        self.tree = Treeview(self,
                             columns = self.headers,
                             show = 'headings')  # 不写show="headings"会空一列
        for head in self.headers:
            self.tree.column(head, anchor = "center")
            self.tree.heading(head, text = head)
        self.tree.grid(row = 0, sticky = tk.NSEW)

        # 添加垂直滚动条
        vbar = Scrollbar(self, orient = 'vertical', command = self.tree.yview)
        self.tree.configure(yscrollcommand = vbar.set)
        vbar.grid(row = 0, column = 1, sticky = tk.NS)

        # 双击显示详细信息
        self.tree.bind('<Double-Button-1>', lambda e: self.showItem())

    def createForm(self, data: List[List]) -> None:
        """
        搜索结果输入到结果框中，data = [(index, (title, authors, date, publication, abstract, doi, web))]
        """
        self.clearForm()
        for i, item in data:
            self.tree.insert("", i, values = item)

    def clearForm(self) -> None:
        for item in self.tree.get_children():
            self.tree.delete(item)

    def showItem(self) -> None:
        detail = self.tree.item(self.tree.selection(), "values")
        DetailWindow(detail)
