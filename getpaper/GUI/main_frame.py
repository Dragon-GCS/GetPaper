import logging
import time
import tkinter as tk
from queue import PriorityQueue, Queue
from tkinter.ttk import Button, Combobox, Entry, Frame, Label, Progressbar, Spinbox

from getpaper.config import (DEFAULT_SCI_HUB_URL, SORTED_BY, TIMEOUT, TIP_REFRESH, spider_list)
from getpaper.utils import MyThread, TipException, getQueueData, setSpider, startThread
from getpaper.spiders._spider import _Spider

log = logging.getLogger("GetPaper")

class TipFrame(Frame):
    def __init__(self, master: tk.Widget) -> None:
        super().__init__(master)
        self.columnconfigure(1, weight = 1)
        self.label = Label(self, text = "进度", width = 16, anchor = "e")
        self.label.grid(row = 0, column = 0, sticky = tk.E)
        self.bar = Progressbar(self, style = "info.Striped.Horizontal.TProgressbar")
        self.bar.grid(row = 0, column = 1, sticky = tk.EW)

    def setTip(self, text: str) -> None:
        self.label["text"] = text


class MainFrame(Frame):
    spider: _Spider
    def __init__(self, master: tk.Widget, result_frame: tk.Widget, **kwargs):
        super().__init__(master, **kwargs)
        self.grid(row = 0, sticky = tk.EW)
        self.result_frame = result_frame
        self.columnconfigure(0, weight = 1)

        # Create a frame for each rows
        self.row_1 = Frame(self, **kwargs)
        self.row_2 = Frame(self, **kwargs)
        self.row_3 = Frame(self, **kwargs)
        self.row_4 = Frame(self, **kwargs)
        for row in range(1, 5):
            setattr(self, f"row_{row}", Frame(self, **kwargs))
            getattr(self, f"row_{row}").grid(row = row, sticky = tk.EW)
            getattr(self, f"row_{row}").rowconfigure(0, weight = 1)

            for i in range(20):
                getattr(self, f"row_{row}").columnconfigure(i + 1, weight = 1)

        ###################### Row 1st start ######################
        Label(self.row_1, text = "查询数据库：").grid(row = 0, column = 0, sticky = tk.E)
        # Choose a database to search
        self.engine = Combobox(self.row_1, values = spider_list, state = "readonly")
        # Bind a function which can remove the ugly background after select
        self.engine.bind("<<ComboboxSelected>>", lambda e: self.engine.selection_clear())
        self.engine.grid(row = 0, column = 1, sticky = tk.W)
        # Available url of Sci-Hub
        Label(self.row_1, text = "如需下载文献请在此输入可用的SciHub网址：https：//").grid(row = 0, column = 20, sticky = "e")
        self.scihub_url = Entry(self.row_1)
        self.scihub_url.insert(0, DEFAULT_SCI_HUB_URL)
        self.scihub_url.grid(row = 0, column = 21, sticky = tk.W)
        ####################### Row 1st end #######################

        ###################### Row 2nd start ######################
        # Keywords
        Label(self.row_2, text = "请输入查询关键词：", width = 16, anchor = "e").grid(row = 0, column = 0, sticky = tk.E)
        self.keyword = Entry(self.row_2)
        self.keyword.grid(row = 0, column = 1, columnspan = 15, sticky = tk.EW)
        self.keyword.focus()
        # Start year of search
        Label(self.row_2, text = "开始时间").grid(row = 0, column = 18, sticky = tk.E)
        self.start_year = Spinbox(self.row_2, from_ = 1900, to = 2022)
        self.start_year.grid(row = 0, column = 19, sticky = tk.W)
        # End year of search
        Label(self.row_2, text = "截至时间").grid(row = 0, column = 20, sticky = tk.E)
        self.end_year = Spinbox(self.row_2, from_ = 1900, to = 2022)
        self.end_year.grid(row = 0, column = 21, sticky = tk.W)
        ####################### Row 2nd end #######################

        ###################### Row 3rd start ######################
        # Author
        Label(self.row_3, text = "作者：", width = 16, anchor = "e").grid(row = 0, column = 0, sticky = tk.E)
        self.author = Entry(self.row_3)
        self.author.grid(row = 0, column = 1, sticky = tk.W)
        # Publication
        Label(self.row_3, text = "期刊：").grid(row = 0, column = 11, sticky = tk.E)
        self.journal = Entry(self.row_3)
        self.journal.grid(row = 0, column = 12, sticky = tk.W)
        # Sort order of search result
        Label(self.row_3, text = "排序方式").grid(row = 0, column = 20, sticky = tk.E)
        self.sorting = Combobox(self.row_3, values = SORTED_BY, state = "readonly")
        self.sorting.current(0)
        self.sorting.bind("<<ComboboxSelected>>", lambda e: self.sorting.selection_clear())
        self.sorting.grid(row = 0, column = 21, sticky = tk.W)
        ####################### Row 3rd end #######################

        ###################### Row 4th start ######################
        # Search button
        self.search_button = Button(self.row_4, text = "关键词搜索", command = self.search, width = 10)
        self.search_button.grid(row = 0, column = 0)
        self.tip = TipFrame(self.row_4)
        self.tip.grid(row = 0, column = 3, columnspan = 15)
        # Choose the quantity of search
        Label(self.row_4, text = "请输入需要获取的文献数量：").grid(row = 0, column = 19, sticky = tk.E)
        self.num = Entry(self.row_4)
        self.num.insert(0, "0")
        self.num.grid(row = 0, column = 20, sticky = tk.W)
        # Download button
        self.download_button = Button(self.row_4, text = "获取详情", command = self.getDetail, width = 10)
        self.download_button.grid(row = 0, column = 21)
        ####################### Row 4th end #######################

    @setSpider
    @startThread("Search")
    def search(self) -> None:
        """Get the total number of search result """

        self.search_button.state(["disabled"])
        self.tip.setTip("搜索中")
        self.tip.bar.start()
        try:
            t = MyThread(tip_set = self.tip.setTip,
                         target = self.spider.getTotalPaperNum,
                         **{"name" : f"{self.engine.get()} Get_Num"})
            t. start()
            t.join()
            if t.result:
                self.tip.setTip(t.result)
        except Exception as e:
            log.error(e)
        finally:
            self.tip.bar.stop()
            self.search_button.state(["!disabled"])

    @setSpider
    @startThread("FetchDetail")
    def getDetail(self) -> None:
        """
        Download paper details, include:
        Title, Authors, Date, Publication, Abstract, doi, Url
        """

        self.download_button.state(["disabled"])
        self.tip.setTip("准备中...")
        result = PriorityQueue()
        try:
            num = int(self.num.get())
            if num < 1:
                self.tip.setTip("文献数不为正整数")
                return
            # create a Queue to store result
            log.info(f"Fetch num: {num}")
            result.maxsize = num
            # Start task on new thread 
            # tip_set function for catching TipException show on GUI
            MyThread(tip_set=self.tip.setTip,
                     target=self.spider.getAllPapers,
                     args=(result, num),
                     name=f"{self.engine.get()} Fetch"
                     ).start()

            self.monitor(result, num)
        except Exception as e:
            log.error(e)
        else:
            self.tip.setTip("获取结束")
        finally:
            size = 0
            self.tip.bar.stop()
            try:
                if not result.empty():
                    size = result.qsize()
                    self.result = getQueueData(result)
                    # get item from queue and send all to result frame
                    self.result_frame.createForm(self.result)  # type: ignore
            finally:
                self.download_button.state(["!disabled"])
                self.tip.setTip(f"抓取完成， 共{size}篇")

    def monitor(self, monitor_queue: Queue, total: int) -> None:
        """
        Monitor progress by the size of Queue, progress = queue.qsize / total
        Args:
            monitor_queue: Queue to monitor.
            total: the max size of the Queue
        """

        # start progress bar
        start = time.time()
        size = 0
        while True:
            current_size = monitor_queue.qsize()
            if current_size == size:
                if time.time() - start > TIMEOUT:
                    raise TipException("连接超时")
            elif monitor_queue.full():
                break
            else:
                start = time.time()
                size = current_size
                self.tip.setTip(f"下载中：{current_size}/{total}")
                self.tip.bar["value"] = 100 * current_size / total
            time.sleep(TIP_REFRESH)
