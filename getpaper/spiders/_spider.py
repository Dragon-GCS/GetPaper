import asyncio
from abc import ABC, abstractmethod
from queue import PriorityQueue
from typing import Any, Dict

from aiohttp import ClientSession

from getpaper.utils import TipException


class _Spider(ABC):
    base_url: str

    def __init__(self, keyword: str = "",
                 start_year: str = "",
                 end_year: str = "",
                 author: str = "",
                 journal: str = "",
                 sorting: str = "") -> None:
        """
        Base spider
        Args:
            keyword: keyword, split by space
            start_year: default to 1900
            end_year: default to next year
            author: filter by author, default to None
            journal: filter by published journal, default to None
            sorting: sorting result by details or match
        """
        self.data = self.parseData(keyword, start_year, end_year, author, journal, sorting)

    async def getHtml(self, session: ClientSession, params: Dict[str, Any]) -> str:
        """Async get html"""
        try:
            async with session.get(self.base_url, params = params) as response:
                print("Get url: ", response.url)
                html = await response.text()
            return html
        except asyncio.exceptions.TimeoutError:
            raise TipException("连接超时")

    @abstractmethod
    def parseData(self, keyword: str,
                  start_year: str,
                  end_year: str,
                  author: str,
                  journal: str,
                  sorting: str) -> Dict[str, Any]:
        """format details to search format"""
        return {}

    @abstractmethod
    def getTotalPaperNum(self) -> None:
        """
        Get the total number of result
        Returns:
            num: number of search result
        """
        pass

    @abstractmethod
    def getAllPapers(self, queue: PriorityQueue, num: int) -> None:
        """
        Get all papers detail
        Params:
            queue: a process queue for storing result and feedbacking progess,
                details format is [index, (title, authors, date, publication, abstract, doi, web)]
            num: number of papers to get
        """
        pass
