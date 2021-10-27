import re
from typing import List, Protocol, Tuple, Union

from getpaper.utils import AsyncFunc


def generateFilename(filename):
    return re.sub(r"[:\?\\/\*\|\"\<\>]", "", filename)


class Downloader(Protocol):
    def download(self) -> None:
        ...

    def multidownload(self) -> None:
        ...


class SciHubDownloader:
    def __init__(self, url: str) -> None:
        if not url.startswith("https"):
            url = "https://" + url
        self.url = url
        print(self.url)

    @AsyncFunc
    def download(self, doi: str, filename: str = None) -> None:
        pass

    def multidownload(self, data: Union[Tuple, List]) -> None:
        for title, *_, doi, __ in data:
            filename = generateFilename(title)
            self.download(doi, title)
