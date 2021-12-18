import asyncio
import logging
import os
import re
from queue import Queue
from typing import Any, Optional
from typing import Protocol, Sequence

import aiohttp
from bs4 import BeautifulSoup

from getpaper.config import SCI_DELAY
from getpaper.utils import AsyncFunc, getSession

log = logging.getLogger("GetPaper")

def checkFilename(filename: str, suffix: str = ".pdf"):
    """
    Check whether the filename contains invalid character.
    Add suffix automatically if filname doesn't ends with specified suffix.
    Args:
        filename: filename to save, not recommended contains path
        suffix: the specified string at the end of filename
    Returns:
        returns: filename without invalid character and ends with specified suffix
    """
    valid_name = re.sub(r"[:?/*|<>\"\\]", "", filename).rstrip(".")
    if not valid_name.endswith(suffix):
        valid_name += suffix
    return valid_name


class Downloader(Protocol):
    def download(self, doi: str, filename: str = "") -> Any:
        ...

    def multiDownload(self, details: Sequence[Sequence[str]], monitor: Queue, target_dir: str = "") -> Any:
        ...


class SciHubDownloader:
    def __init__(self, url: str) -> None:
        self.monitor: Optional[Queue] = None
        self.session: Optional[aiohttp.ClientSession] = None

        if not url.startswith("https"):
            url = "https://" + url
        self.url = url

    async def _download(self, doi: str, filename: str, index: int = 0) -> None:
        """
        From Sci-Hub download pdf by doi.
        Args:
            doi: the doi of paper, from search result.
            filename: name of downloaded pdf file.
            index: index of doi, download will be delayed by index * SCI_DELAY second.
        """

        url = f"{self.url}/{doi}"
        content: bytes = b''
        flag: bool = False # success to find pdf url or not
        base, filename = os.path.split(filename)
        error_name = filename

        log.debug(f"Downloading doi: {doi}")
        await asyncio.sleep(index * SCI_DELAY)  # add delay

        if doi:
            for _ in range(3):
                # try 3 times for download
                try:
                    async with self.session.get(url) as response:
                        bs = BeautifulSoup(await response.text(), "lxml")
                        if pdf := bs.find("iframe", id = "pdf"):
                            async with self.session.get(pdf["src"].split("#")[0]) as result:
                                content = await result.read()
                                flag = True
                        else:
                            content = f"Sci-Hub has not yet included this paper\ndoi: {doi}".encode("utf-8")
                        break

                except asyncio.exceptions.TimeoutError:
                    content = f"Connect timeout\n{filename}\nURL: {url}".encode("utf-8")
                    log.debug(f"Connect timeout\nURL: {url}")

                    if not error_name.startswith("Timeout_"):
                        error_name = "Timeout_" + filename

                except Exception as e:
                    content = f"Unknown Error\n{filename}\nURL: {url}".encode("utf-8")
                    log.error(f"Error URL: {url} ", e)

                    if not error_name.startswith("ERROR_"):
                        error_name = "ERROR_" + filename

        else:
            content = f"{filename.rstrip('.pdf')}\nNot found doi".encode("utf-8")
            error_name = "NotFound_" + error_name

        if not flag:
            # use error name to save file
            filename = error_name.replace(".pdf", ".txt")

        with open(os.path.join(base, filename), "wb") as f:
            f.write(content)

        if getattr(self, "monitor", None) is not None:
            self.monitor.put((filename, flag))

        log.debug(f"Download finish: {filename}")

    @AsyncFunc
    async def download(self, doi: str, filename: str = "") -> None:
        """
        Download single paper from sci-hub by doi and save to filename.
        Args:
            doi: the doi of paper, from search result.
            filename: name of downloaded pdf file.
        """

        if getattr(self, "session", None) is None:
            self.session = getSession()

        await self._download(doi, filename)
        if hasattr(self, "session"):
            try:
                await self.session.close()
            finally:
                del self.session

    @AsyncFunc
    async def multiDownload(self, details: Sequence[Sequence[str]], 
                            monitor: Queue = None,
                            target_dir: str = "") -> None:
        """
        Download multiple paper from sci-hub by doi, filename defaults to title.
        Args:
            details: A sequences include all search result, title is details[0], doi is details[-2]
            monitor：A Queue for monitoring the download progress by monitor.qsize() / monitor.max_size
            target_dir: Directory to save all PDFs.
        """

        self.monitor = monitor

        if getattr(self, "session", None) is None:
            self.session = getSession()

        if not os.path.isdir(target_dir):
            os.makedirs(target_dir)

        task = []
        for index, (title, *_, doi, __) in enumerate(details) :
            valid_name = checkFilename(title)
            filename = os.path.join(target_dir, valid_name)
            task.append(self._download(doi, filename, index = index))

        await asyncio.gather(*task)

        if hasattr(self, "session"):
            try:
                await self.session.close()
            finally:
                del self.session


if __name__ == "__main__":
    data = [["A hierarchical Bayesian approach for detecting global microbiome associations", "Authors", "Date",
             "Publication", "Abstract", "10.1126/science.2470152", "Url"],
            ["Risk factors for heat-related illnesses during the Hajj mass gathering: an expert review.", "Authors",
             "Date", "Publication", "Abstract", "10.1126/science.2470152", "Url"],
            ["COVID-19 disease in clinical setting: impact on gonadal function, transmission risk, and sperm quality "
             "in young males.", "Authors", "Date", "Publication", "Abstract", "10.1126/science.2470152", "Url"]
            ]

    downloader = SciHubDownloader("sci-hub.ren")
    downloader.download(data[0][-2], checkFilename("test"))
    downloader.multiDownload(data, Queue(), "test")
