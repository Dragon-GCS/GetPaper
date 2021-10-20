from threading import Thread
import tkinter as tk
from tkinter import ttk
from tkinter import font
from tkinter.ttk import Frame, Label, Combobox, Entry, Button, Progressbar, Spinbox, Treeview
from typing import Iterable, List, Union
from ttkbootstrap import Style

from getpaper.config import APP_NAME
from getpaper.utils import getSpider, getSpiderList


class TipFrame(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.grid(sticky = tk.EW)
        self.columnconfigure(1, weight=1)
        self.label = Label(self, width=12, anchor="e")
        self.label.grid(row = 0, column = 0, sticky=tk.E)
        self.bar = Progressbar(self, style="info.Striped.Horizontal.TProgressbar")

    def showBar(self):
        self.bar.grid(row = 0, column = 1, sticky=tk.EW)
    
    def setTip(self, text):
        self.label["text"] = text


class MainFrame(ttk.Frame):
    def __init__(self, master: Frame, result_frame: Frame, **kwargs):
        super().__init__(master, **kwargs)
        self.grid(row = 0, sticky = tk.EW)
        self.result_frame = result_frame
        self.columnconfigure(0, weight=1)

        # 每行生成一个Frame
        for row in range(4):
            setattr(self, f"row_{row + 1}", Frame(self, **kwargs))
            getattr(self, f"row_{row + 1}").grid(row = row, sticky = tk.EW)
            getattr(self, f"row_{row + 1}").rowconfigure(0, weight=1)
        
            for i in range(20):
                getattr(self, f"row_{row + 1}").columnconfigure(i+1, weight=1)

        # 第一行： 选择数据库； 输入Sci-Hub地址
        Label(self.row_1, text = '查询数据库：').grid(row = 0, column = 0, sticky=tk.E)
        # 选择数据库
        self.engine = Combobox(self.row_1, values = getSpiderList(), state="readonly")
        # 绑定方法，消除选择后的文字背景
        self.engine.bind('<<ComboboxSelected>>', lambda e:self.engine.selection_clear())
        self.engine.grid(row = 0, column = 1, sticky=tk.W)

        Label(self.row_1, text = "如需下载文献请在此输入可用的SciHub网址：https：//").grid(row = 0, column = 20, sticky='e')
        # Sci-Hub网址
        self.scihub_url = Entry(self.row_1)
        self.scihub_url.insert(0, "sci-hub.ren")
        self.scihub_url.grid(row = 0, column = 21, sticky=tk.W)

        # 第二行： 输入关键词；选择查找时间范围
        Label(self.row_2, text = "请输入查询关键词：", width=16, anchor="e").grid(row=0, column=0, sticky=tk.E)
        # 关键词
        self.keyword = Entry(self.row_2)
        self.keyword.grid(row=0, column=1,columnspan=15, sticky=tk.EW)
        self.keyword.focus()
        # 起始年份
        Label(self.row_2, text = "开始时间").grid(row=0, column=18, sticky=tk.E)
        self.start_year = Spinbox(self.row_2, from_=1900, to=2022)
        self.start_year.grid(row=0, column=19, sticky=tk.W)
        # 截止时间
        Label(self.row_2, text = "截至时间").grid(row = 0, column = 20, sticky=tk.E)
        self.end_year = Spinbox(self.row_2, from_ = 1900, to = 2022)
        self.end_year.grid(row = 0, column = 21, sticky=tk.W)

        # 第三行： 作者；期刊；排序方式
        Label(self.row_3, text = "作者：", width=16, anchor="e").grid(row=0, column=0, sticky=tk.E)
        self.author = Entry(self.row_3)
        self.author.grid(row=0, column=1, sticky=tk.W)
        Label(self.row_3, text = "期刊：").grid(row = 0, column = 11, sticky=tk.E)
        self.journal = Entry(self.row_3)
        self.journal.grid(row = 0, column = 12, sticky=tk.W)
        Label(self.row_3, text = "排序方式").grid(row = 0, column = 20, sticky=tk.E)
        self.sorted = Combobox(self.row_3, values = ["相关性", "日期", "日期逆序"], state="readonly")
        self.sorted.bind('<<ComboboxSelected>>', lambda e:self.sorted.selection_clear())
        self.sorted.grid(row = 0, column = 21, sticky=tk.W)

        # 第四行：搜索；搜索进度；下载
        Button(self.row_4, text = "搜索", command = self.search, width=10).grid(row = 0, column = 0)
        self.tip = TipFrame(self.row_4)
        self.tip.grid(row=0, column=3, columnspan=15)
        Label(self.row_4, text = "请输入需要下载的文献数量：").grid(row = 0, column = 19, sticky=tk.E)
        self.num = Entry(self.row_4)
        self.num.grid(row = 0, column = 20, sticky = tk.W)
        Button(self.row_4, text = "下载", command = self.download, width=10).grid(row = 0, column = 21)
        ########## 测试按钮 ##########
        Button(self, text="insert", command=self.test1).grid()
        Button(self, text="clear", command=self.test2).grid()
        self.data = [[str(i)] * 5 for i in range(10)]
        ########## 测试按钮 ##########
    ########## 测试函数 ##########
    def test1(self):
        self.result_frame.createForm(self.data)
    def test2(self):
        self.result_frame.clearForm()
    ########## 测试函数 ##########
    def search(self):
        import time
        from threading import Thread
        def _():
            self.tip.bar.start()
            self.tip.setTip("搜索中")
            self.tip.showBar()
            time.sleep(11)
            self.tip.bar.stop()
            self.tip.setTip("搜索完成")
        Thread(target=_).start()
    
    def download(self):
        def _():
            import time
            from threading import Thread
            
            self.tip.showBar()
            a = 1
            while a <= 100:
                self.tip.setTip(f"下载中：{a}/100")
                time.sleep(0.1) 
                self.tip.bar["value"] = a
                a += 1
            self.tip.setTip("下载完成")

        Thread(target=_).start()


class ResultFrame(ttk.Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.grid(row = 1, sticky = tk.NSEW)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        # 设置表头
        self.headers = ('标题', '作者', '发表时间', '期刊', '摘要')
        self.tree = Treeview(self, columns=self.headers, show='headings')   # 不写show="headings"会空一列
        for head in self.headers:
            self.tree.column(head, anchor="center")
            self.tree.heading(head, text=head)
        self.tree.grid(row = 0, sticky=tk.NSEW)

        # 添加垂直滚动条
        vbar = ttk.Scrollbar(self, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=vbar.set)
        vbar.grid(row=0, column=1, sticky=tk.NS)

        # 双击显示详细信息
        self.tree.bind('<Double-Button-1>', lambda e: self.showItem())

    def createForm(self, data:List[List] ):
        for i, item in enumerate(data):
            self.tree.insert("", i, values = item)
    
    def clearForm(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

    def showItem(self):
        detail = self.tree.item(self.tree.selection(), "values")
        detail_window = DetailWindow(detail)
        


class DetailWindow(tk.Toplevel):
    def __init__(self, detail):
        super().__init__()
        self.title = "文章详情"
        self.label = tk.Text(self, font="微软雅黑 12")
        # https://tkdocs.com/shipman/text-index.html
        self.label.insert(index='insert', chars="\n".join(detail))
        self.label.grid()

class Application(Style):
    def __init__(self, theme):
        super().__init__(theme)
        self.master.title(APP_NAME)
        self.master.minsize(960,600)

        self.master.columnconfigure(0, weight=1)    # 第一列随宽度变化
        self.master.rowconfigure(1, weight=1)       # 第二行随高度变化

        self.result_frame = ResultFrame(self.master, relief = "ridge")
        self.main_frame = MainFrame(self.master, self.result_frame, relief = "ridge", padding = 10)

        self.master.option_add("*Font", "微软雅黑 12")
        style = ttk.Style()
        style.configure('TButton', font=('微软雅黑', 12))
        style.configure('Treeview', font='微软雅黑')
        style.configure('Treeview.Heading', font=('微软雅黑', 12))

        

    def run(self):
        self.master.mainloop()


if __name__ == "__main__":
    app = Application("flatly")
    app.run()