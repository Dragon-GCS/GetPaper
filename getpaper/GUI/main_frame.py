import asyncio
import logging
from contextlib import suppress
from queue import PriorityQueue, Queue
from tkinter import Event
from typing import ClassVar

import ttkbootstrap as ttk
from ttkbootstrap import Button, Combobox, Entry, Frame, Label, Spinbox, constants

from getpaper.config import DEFAULT_SCI_HUB_URL, SORTED_BY, TIP_REFRESH, spider_list
from getpaper.GUI.result_frame import ResultFrame
from getpaper.GUI.tip_frame import TipFrame
from getpaper.spiders._spider import PaperDetail, _Spider
from getpaper.utils import getSpider, startTask

log = logging.getLogger("GetPaper")


class MainFrame(Frame):
    spider: _Spider
    result: ClassVar[list[PaperDetail]] = []
    total_num: int

    def __init__(self, master: ttk.Window, result_frame: ResultFrame, **kwargs):
        super().__init__(master, **kwargs)
        self.grid(row=0, sticky=constants.EW)
        self.result_frame = result_frame
        self.columnconfigure(0, weight=1)

        # Create a frame for each rows
        self.row_1: Frame
        self.row_2: Frame
        self.row_3: Frame
        self.row_4: Frame
        for row in range(1, 5):
            frame = Frame(self, **kwargs)
            frame.grid(row=row, sticky=constants.EW)
            frame.rowconfigure(0, weight=1)
            for i in range(20):
                frame.columnconfigure(i + 1, weight=1)
            setattr(self, f"row_{row}", frame)

        ###################### Row 1st start ######################
        Label(self.row_1, text="查询数据库：").grid(row=0, column=0, sticky=constants.E)
        # Choose a database to search
        self.engine = Combobox(self.row_1, values=spider_list, state="readonly")
        # Bind a function which can remove the ugly background after select
        self.engine.bind("<<ComboboxSelected>>", self.selectSpider)
        self.engine.grid(row=0, column=1, sticky=constants.W)
        self.engine.selection_clear()
        # Available url of Sci-Hub
        Label(self.row_1, text="如需下载文献请在此输入可用的SciHub网址：https：//").grid(
            row=0, column=20, sticky=constants.E
        )
        self.scihub_url = Entry(self.row_1)
        self.scihub_url.insert(0, DEFAULT_SCI_HUB_URL)
        self.scihub_url.grid(row=0, column=21, sticky=constants.W)
        ####################### Row 1st end #######################

        ###################### Row 2nd start ######################
        # Keywords
        Label(self.row_2, text="请输入查询关键词：", width=16, anchor="e").grid(
            row=0, column=0, sticky=constants.E
        )
        self.keyword = Entry(self.row_2)
        self.keyword.grid(row=0, column=1, columnspan=15, sticky=constants.EW)
        self.keyword.focus()
        # Start year of search
        Label(self.row_2, text="开始时间").grid(row=0, column=18, sticky=constants.E)
        self.start_year = Spinbox(self.row_2, from_=1900, to=2022)
        self.start_year.grid(row=0, column=19, sticky=constants.W)
        # End year of search
        Label(self.row_2, text="截至时间").grid(row=0, column=20, sticky=constants.E)
        self.end_year = Spinbox(self.row_2, from_=1900, to=2022)
        self.end_year.grid(row=0, column=21, sticky=constants.W)
        ####################### Row 2nd end #######################

        ###################### Row 3rd start ######################
        # Author
        Label(self.row_3, text="作者：", width=16, anchor="e").grid(
            row=0, column=0, sticky=constants.E
        )
        self.author = Entry(self.row_3)
        self.author.grid(row=0, column=1, sticky=constants.W)
        # Publication
        Label(self.row_3, text="期刊：").grid(row=0, column=11, sticky=constants.E)
        self.journal = Entry(self.row_3)
        self.journal.grid(row=0, column=12, sticky=constants.W)
        # Sort order of search result
        Label(self.row_3, text="排序方式").grid(row=0, column=20, sticky=constants.E)
        self.sorting = Combobox(self.row_3, values=SORTED_BY, state="readonly")
        self.sorting.current(0)
        self.sorting.bind("<<ComboboxSelected>>", lambda e: self.sorting.selection_clear())
        self.sorting.grid(row=0, column=21, sticky=constants.W)
        ####################### Row 3rd end #######################

        ###################### Row 4th start ######################
        # Search button
        self.search_button = Button(self.row_4, text="关键词搜索", command=self.search, width=10)
        self.search_button.grid(row=0, column=0)
        self.tip = TipFrame(self.row_4)
        self.tip.grid(row=0, column=3, columnspan=15)
        # Choose the quantity of search
        Label(self.row_4, text="请输入需要获取的文献数量：").grid(
            row=0, column=19, sticky=constants.E
        )
        self.num = Entry(self.row_4)
        self.num.insert(0, "0")
        self.num.grid(row=0, column=20, sticky=constants.W)
        # Download button
        self.download_button = Button(self.row_4, text="获取详情", command=self.getDetail, width=10)
        self.download_button.grid(row=0, column=21)
        ####################### Row 4th end #######################

    def selectSpider(self, event: Event) -> None:
        if not self.engine.get():
            self.tip.setTip("未选择搜索引擎")
            return
        self.spider = getSpider(
            name=self.engine.get(),
            keyword=self.keyword.get(),
            start_year=self.start_year.get(),
            end_year=self.end_year.get(),
            author=self.author.get(),
            journal=self.journal.get(),
            sorting=self.sorting.get(),
        )
        log.info(f"Init this spider: {self.engine.get()}")
        self.engine.selection_clear()

    @startTask("Search")
    async def search(self) -> None:
        """Get the total number of search result"""

        self.search_button.state(["disabled"])
        self.tip.setTip("搜索中")
        self.tip.bar.start()
        try:
            self.spider.parseData(
                keyword=self.keyword.get(),
                start_year=self.start_year.get(),
                end_year=self.end_year.get(),
                author=self.author.get(),
                journal=self.journal.get(),
                sorting=self.sorting.get(),
            )
            result = await self.spider.getTotalPaperNum()
            self.tip.setTip(f"共找到{result}篇文献")
            self.total_num = result
            self.num.delete(0, "end")
            self.num.insert(0, str(result))
        except Exception:
            log.exception("Setting spider error")
            self.tip.setTip("搜索出错")
        finally:
            self.tip.bar.stop()
            self.search_button.state(["!disabled"])

    @startTask("FetchDetail")
    async def getDetail(self) -> None:
        """
        Download paper details, include:
        Title, Authors, Date, Publication, Abstract, doi, Url
        """

        self.download_button.state(["disabled"])
        self.tip.setTip("准备中...")
        num = min(max(0, int(self.num.get())), self.total_num)
        log.info(f"Fetch num: {num}")
        result = PriorityQueue(num)

        monitor_task = asyncio.create_task(
            self.monitor(result, num), name=f"{self.engine.get()} Fetch"
        )
        try:
            await self.spider.getAllPapers(result, num)
        except Exception:
            log.exception("Get Detail Error")
            self.tip.setTip("获取详情出错")
        finally:
            monitor_task.cancel()
            self.tip.setTip("获取结束")
            self.result.clear()
            while not result.empty():
                self.result.append(result.get()[1])
            self.tip.setTip(f"抓取完成， 共{len(self.result)}篇")

        with suppress(asyncio.CancelledError):
            await monitor_task
        self.tip.bar.stop()
        self.result_frame.createForm(self.result)
        self.download_button.state(["!disabled"])

    async def monitor(self, monitor_queue: Queue, total: int) -> None:
        """
        Monitor progress by the size of Queue, progress = queue.qsize / total
        Args:
            monitor_queue: Queue to monitor.
            total: the max size of the Queue
        """

        # start progress bar
        while not monitor_queue.full():
            size = monitor_queue.qsize()
            self.tip.setTip(f"下载中：{size}/{total}")
            self.tip.bar["value"] = 100 * size / total
            await asyncio.sleep(TIP_REFRESH)
