import time
import tkinter as tk
from multiprocessing import Pool, Process, Queue
from tkinter.ttk import Button, Combobox, Entry, Frame, Label, Progressbar, Spinbox

from getpaper.config import SORTED_BY, spider_list
from getpaper.utils import getSortedData, startThread


class TipFrame(Frame):
    def __init__(self, master):
        super().__init__(master)
        self.grid(sticky = tk.EW)
        self.columnconfigure(1, weight = 1)
        self.label = Label(self, text = "进度", width = 16, anchor = "e")
        self.label.grid(row = 0, column = 0, sticky = tk.E)
        self.bar = Progressbar(self, style = "info.Striped.Horizontal.TProgressbar")
        self.bar.grid(row = 0, column = 1, sticky = tk.EW)

    def setTip(self, text):
        self.label["text"] = text


class MainFrame(Frame):
    def __init__(self, master: Frame, result_frame: Frame, **kwargs):
        super().__init__(master, **kwargs)
        self.grid(row = 0, sticky = tk.EW)
        self.result_frame = result_frame
        self.columnconfigure(0, weight = 1)

        # 每行生成一个Frame
        for row in range(4):
            setattr(self, f"row_{row + 1}", Frame(self, **kwargs))
            getattr(self, f"row_{row + 1}").grid(row = row, sticky = tk.EW)
            getattr(self, f"row_{row + 1}").rowconfigure(0, weight = 1)

            for i in range(20):
                getattr(self, f"row_{row + 1}").columnconfigure(i + 1, weight = 1)

        ###################### 第一行开始 ######################
        Label(self.row_1, text = '查询数据库：').grid(row = 0, column = 0, sticky = tk.E)
        # 选择数据库
        self.engine = Combobox(self.row_1, values = spider_list, state = "readonly")
        self.spider = None
        # 绑定方法，消除选择后的文字背景
        self.engine.bind('<<ComboboxSelected>>', lambda e: self.engine.selection_clear())
        self.engine.grid(row = 0, column = 1, sticky = tk.W)
        # Sci-Hub网址
        Label(self.row_1, text = "如需下载文献请在此输入可用的SciHub网址：https：//").grid(row = 0, column = 20, sticky = 'e')
        self.scihub_url = Entry(self.row_1)
        self.scihub_url.insert(0, "sci-hub.ren")
        self.scihub_url.grid(row = 0, column = 21, sticky = tk.W)
        ###################### 第一行结束 ######################

        ###################### 第二行开始 ######################
        # 关键词
        Label(self.row_2, text = "请输入查询关键词：", width = 16, anchor = "e").grid(row = 0, column = 0, sticky = tk.E)
        self.keyword = Entry(self.row_2)
        self.keyword.grid(row = 0, column = 1, columnspan = 15, sticky = tk.EW)
        self.keyword.focus()
        # 起始年份
        Label(self.row_2, text = "开始时间").grid(row = 0, column = 18, sticky = tk.E)
        self.start_year = Spinbox(self.row_2, from_ = 1900, to = 2022)
        self.start_year.grid(row = 0, column = 19, sticky = tk.W)
        # 截止时间
        Label(self.row_2, text = "截至时间").grid(row = 0, column = 20, sticky = tk.E)
        self.end_year = Spinbox(self.row_2, from_ = 1900, to = 2022)
        self.end_year.grid(row = 0, column = 21, sticky = tk.W)
        ###################### 第二行结束 ######################

        ###################### 第三行开始 ######################
        # 作者
        Label(self.row_3, text = "作者：", width = 16, anchor = "e").grid(row = 0, column = 0, sticky = tk.E)
        self.author = Entry(self.row_3)
        self.author.grid(row = 0, column = 1, sticky = tk.W)
        # 期刊
        Label(self.row_3, text = "期刊：").grid(row = 0, column = 11, sticky = tk.E)
        self.journal = Entry(self.row_3)
        self.journal.grid(row = 0, column = 12, sticky = tk.W)
        # 排序方式
        Label(self.row_3, text = "排序方式").grid(row = 0, column = 20, sticky = tk.E)
        self.sorting = Combobox(self.row_3, values = SORTED_BY, state = "readonly")
        self.sorting.current(0)
        self.sorting.bind('<<ComboboxSelected>>', lambda e: self.sorting.selection_clear())
        self.sorting.grid(row = 0, column = 21, sticky = tk.W)
        ###################### 第三行结束 ######################

        ###################### 第四行开始 ######################
        # 搜索按钮
        self.search_button = Button(self.row_4, text = "关键词搜索", command = self.search, width = 10)
        self.search_button.grid(row = 0, column = 0)
        self.tip = TipFrame(self.row_4)
        self.tip.grid(row = 0, column = 3, columnspan = 15)
        # 选择文献数量
        Label(self.row_4, text = "请输入需要获取的文献数量：").grid(row = 0, column = 19, sticky = tk.E)
        self.num = Entry(self.row_4)
        self.num.insert(0, "0")
        self.num.grid(row = 0, column = 20, sticky = tk.W)
        # 下载按钮
        self.download_button = Button(self.row_4, text = "获取详情", command = self.download, width = 10)
        self.download_button.grid(row = 0, column = 21)
        ###################### 第四行结束 ######################

    @startThread
    def search(self):
        self.search_button.state(["disabled"])
        self.tip.setTip("搜索中")
        self.tip.bar.start()
        try:
            with Pool(1) as pool:
                self.tip.setTip(pool.apply(self.spider.getTotalPaperNum))
        except:
            self.tip.setTip("未知错误")
        finally:
            self.tip.bar.stop()
            self.search_button.state(["!disabled"])

    @startThread
    def download(self):
        self.download_button.state(["disabled"])

        try:
            num = int(self.num.get())
            if num < 1:
                raise ValueError

            result = Queue(num)
            Process(target = self.spider.getAllPapers,
                    args = (result, num),
                    daemon = True).start()

            while not result.full():
                self.tip.setTip(f"下载中：{result.qsize()}/{num}")
                self.tip.bar["value"] = 100 * result.qsize() / num
                time.sleep(0.2)

            self.tip.setTip("下载完成")
            self.result_frame.createForm(getSortedData(result))
        except ValueError:
            self.tip.setTip("文献数不为正整数")
        except Exception as e:
            print(e)
            self.tip.setTip("未知下载错误")

        self.tip.bar.stop()
        self.download_button.state(["!disabled"])
