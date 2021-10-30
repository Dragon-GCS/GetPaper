import asyncio
import os
import re
from queue import Queue
from typing import Any, Optional
from typing import Protocol, Sequence

import aiohttp
from bs4 import BeautifulSoup

from getpaper.utils import AsyncFunc, getSession


def checkFilename(filename: str, suffix: str = ".pdf"):
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

    async def _download(self, doi: str, filename: str) -> None:
        """Download and save to file"""

        url = f"{self.url}/{doi}"
        content: bytes = b''

        try:
            async with self.session.get(url) as response:
                bs = BeautifulSoup(await response.text(), "lxml")
                if pdf := bs.find("iframe", id = "pdf"):
                    async with self.session.get(pdf["src"].split("#")[0]) as result:
                        content = await result.read()
                else:
                    filename += ".txt"
                    content = f"Sci-Hub has not yet included this paper\ndoi: {doi}".encode("utf-8")

        except asyncio.exceptions.TimeoutError:
            filename += ".txt"
            content = f"Connect timeout\nURL: {url}".encode("utf-8")

        except Exception as e:
            print(f"Error URL: {url} ", e)
            filename += ".txt"
            content = f"Unknown Error\nURL: {url}".encode("utf-8")

        finally:
            with open(filename, "wb") as f:
                f.write(content)
            if getattr(self, "monitor", None) is not None:
                self.monitor.put(filename)
            print("Download finish: ", filename)

    @AsyncFunc
    async def download(self, doi: str, filename: str = None) -> None:
        """Download paper by doi from sci-hub, and save as filename"""

        if getattr(self, "session", None) is None:
            self.session = getSession()

        await self._download(doi, filename)

        if hasattr(self, "session"):
            try:
                await self.session.close()
            finally:
                del self.session

    @AsyncFunc
    async def multiDownload(self, details: Sequence[Sequence[str]], monitor: Queue = None,
                            target_dir: str = "") -> None:
        """Download all doi in details, save to file with title as name"""

        self.monitor = monitor

        if getattr(self, "session", None) is None:
            self.session = getSession()

        if not os.path.isdir(target_dir):
            os.makedirs(target_dir)

        task = []
        for title, *_, doi, __ in details:
            valid_name = checkFilename(title)
            filename = os.path.join(target_dir, valid_name)
            task.append(self._download(doi, filename))

        await asyncio.gather(*task)

        if hasattr(self, "session"):
            try:
                await self.session.close()
            finally:
                del self.session


if __name__ == '__main__':
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
