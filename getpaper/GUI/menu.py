import csv
import logging
import webbrowser
from pathlib import Path
from queue import Queue
from tkinter.filedialog import askdirectory, askopenfile, asksaveasfilename
from typing import TYPE_CHECKING

import ttkbootstrap as ttk

from getpaper.config import PROJECT_URL, RESULT_LIST_EN
from getpaper.download import SciHubDownloader
from getpaper.utils import MyThread, startTask

if TYPE_CHECKING:
    from getpaper.GUI.main_frame import MainFrame

log = logging.getLogger("GetPaper")


class MenuBar(ttk.Menu):
    def __init__(self, app):
        """
        Application's MenuBar
        Args:
            app: This application, inherit ttkbootstrap.Style
        """

        super().__init__(app.master)
        # for calling main_frame's function
        self.main_frame: MainFrame = app.main_frame
        self.tip = self.main_frame.tip
        self.add_command(label="数据导出", command=self.saveToFile)
        self.add_command(label="全部下载", command=self.downloadAll)
        self.add_command(label="通过DOI下载", command=self.downloadByDoiFile)
        self.add_command(label="使用说明", command=self.help)

    @startTask("Save_File")
    async def saveToFile(self) -> None:
        """
        Save search result to csv file
        Args:
            filename: Name of csv file to save
        """

        if not hasattr(self.main_frame, "result"):
            # ensure searching has been done
            self.tip.setTip("无搜索结果")
            return

        if filename := asksaveasfilename(defaultextension=".csv", filetypes=[("csv", ".csv")]):
            filename = Path(filename)
            log.info(f"Save file to file: {filename}")
            try:
                with filename.open("w", newline="", encoding="utf-8") as f:
                    writer = csv.writer(f)
                    writer.writerow([s.strip(":\n\t") for s in RESULT_LIST_EN])
                    writer.writerows(self.main_frame.result)
                self.tip.setTip("保存成功")
            except Exception:
                log.exception(f"Save {filename} failed")
                self.tip.setTip("保存失败")

    @startTask("DownloadPapers")
    async def downloadAll(self, details=None) -> None:
        """
        Using SciHubDownloader to get PDFs of all results to specified directory
        Args:
            details: Contain download information. (title, *_, doi, _)
        """
        if not details:
            if not self.main_frame.result:
                self.tip.setTip("无搜索结果")
                return
            details = self.main_frame.result

        if not (target_dir := askdirectory()):
            return

        log.info(f"Downloading all paper to directory: {Path(target_dir).absolute()}")

        self.tip.setTip("准备下载中...")
        monitor_queue = Queue(maxsize=len(details))

        try:
            # create a queue for monitor progress of download
            downloader = SciHubDownloader(self.main_frame.scihub_url.get())
            MyThread(
                tip_set=self.tip.setTip,
                target=downloader.multiDownload,
                args=(details, monitor_queue, target_dir),
                name="Multi-Download",
            ).start()

            await self.main_frame.monitor(monitor_queue, len(details))

        finally:
            self.tip.setTip("下载结束")
            self.tip.bar.stop()

    def downloadByDoiFile(self) -> None:
        """
        Using SciHubDownloader to get PDFs from a txt file, each line represent a doi in this file.
        A detail list is used to call SciHubDownloader.multiDownload():
            detail[0] is paper's title (as save filename), default to doi
            detail[-2] is doi for download
        """

        if file := askopenfile(filetypes=[("文本文件", ".txt")]):
            dois = file.readlines()
            details = []
            log.info(f"Open file: {file.name}\nNumber of lines:{len(dois)}")

            for doi in dois:
                if not doi:
                    continue
                if not doi.startswith("10."):
                    # all valid doi start with "10."
                    continue
                # create a detail list, detail[0] = title(as filename), detail[-2] = doi
                details.append([doi.strip(), None, doi.strip(), None])

            log.info(f"Number of loaded doi: {len(details)}")
            self.downloadAll(details)

    def help(self) -> None:
        webbrowser.open_new_tab(PROJECT_URL)
