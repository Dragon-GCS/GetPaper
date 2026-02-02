import asyncio
import logging
import re
from pathlib import Path
from queue import Queue
from typing import Protocol

from bs4 import BeautifulSoup
from httpx import TimeoutException

from getpaper.config import SCI_DELAY
from getpaper.spiders._spider import PaperDetail
from getpaper.utils import getClient

log = logging.getLogger("GetPaper")


def checkFilename(filename: str, suffix: str = ".pdf"):
    """
    Check whether the filename contains invalid character.
    Add suffix automatically if filename does not ends with specified suffix.
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
    async def download(self, doi: str, monitor: Queue, file: Path, index: int) -> None: ...

    async def multiDownload(
        self, details: list[PaperDetail], monitor: Queue, target_dir: Path
    ) -> None: ...


class SciHubDownloader:
    url: str

    def __init__(self, url: str):
        self.set_url(url)

    def set_url(self, url: str) -> None:
        if not url.startswith("https"):
            url = "https://" + url
        self.url = url.strip("/")

    async def download(self, doi: str, monitor: Queue, file: Path, index: int = 0) -> None:
        """
        Download single paper from sci-hub by doi and save to filename.

        Args:
            doi(str): the doi of paper, from search result.
            file(Path): full path of downloaded pdf file.
            index(int): index of doi, download will be delayed by index * SCI_DELAY second.
        """
        folder, filename = file.parent, file.stem
        if not doi:
            (folder / f"NotFound_{filename}.txt").write_text(f"{file.stem}\nNot found doi")
            return

        log.debug(f"Downloading doi: {doi}")
        await asyncio.sleep(index * SCI_DELAY)  # add delay

        client = getClient()
        url = f"{self.url}/{doi}"
        try:
            response = await client.get(url)
            bs = BeautifulSoup(response.text, "lxml")
            if pdf := bs.find(id="pdf"):
                result = await client.get(pdf["src"].split("#")[0])
                filename += ".pdf"
                content = result.content
            else:
                filename = f"NotIncluded_{filename}.txt"
                content = f"Sci-Hub has not yet included this paper: {doi}".encode("utf-8")
        except TimeoutException:
            content = f"Connect timeout\n{file}\nURL: {url}".encode("utf-8")
            log.exception(f"Connect timeout: {url}")
            filename = f"Timeout_{filename}.txt"
            raise

        except Exception:
            content = f"Unknown error\n{file}\nURL: {url}".encode("utf-8")
            log.exception(f"Unknown error: {url} ")
            filename = f"ERROR_{filename}.txt"
            raise

        (folder / filename).write_bytes(content)
        monitor.put((file, None))
        log.debug(f"Download finish: {file}")

    async def multiDownload(
        self, details: list[PaperDetail], monitor: Queue, target_dir: Path
    ) -> None:
        """
        Download multiple paper from sci-hub by doi, filename defaults to title.

        Args:
            details (list[PaperDetail]): A sequences include all search result, title is details[0], doi is details[-2]
            monitor (Queue): A Queue for monitoring the download progress by monitor.qsize() / monitor.max_size
            target_dir (Path): Directory to save all PDFs.
        """
        target_dir.mkdir(parents=True, exist_ok=True)
        await asyncio.gather(
            *[
                self.download(detail.doi, monitor, target_dir / checkFilename(detail.title), index)
                for index, detail in enumerate(details)
            ]
        )


if __name__ == "__main__":
    data = [
        PaperDetail(
            "A hierarchical Bayesian approach for detecting global microbiome associations",
            "Authors",
            "Date",
            "Publication",
            "Abstract",
            "10.1126/science.2470152",
            "Url",
        ),
        PaperDetail(
            "Risk factors for heat-related illnesses during the Hajj mass gathering: an expert review.",
            "Authors",
            "Date",
            "Publication",
            "Abstract",
            "10.1126/science.2470152",
            "Url",
        ),
        PaperDetail(
            "COVID-19 disease in clinical setting: impact on gonadal function, transmission risk, and sperm quality "
            "in young males.",
            "Authors",
            "Date",
            "Publication",
            "Abstract",
            "10.1126/science.2470152",
            "Url",
        ),
    ]

    async def _main():
        downloader = SciHubDownloader("sci-hub.ren")
        await downloader.download(data[0][-2], Queue(), Path("test"))
        await downloader.multiDownload(data, Queue(), Path("test"))

    asyncio.run(_main())
