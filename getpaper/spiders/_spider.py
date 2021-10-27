import asyncio
from abc import ABC, abstractmethod
from queue import PriorityQueue
from typing import Dict

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
            sorting: sorting result by data or match
        """
        self.data = self.parseData(keyword, start_year, end_year, author, journal, sorting)

    async def getHtml(self, session: ClientSession, params: dict) -> str:
        """Async get html"""
        try:
            response = await session.get(self.base_url, params = params)
            print("Get url: ", response.url)
            return await response.text()
        except asyncio.exceptions.TimeoutError:
            raise TipException("连接超时")

    @abstractmethod
    def parseData(self, keyword: str,
                  start_year: str,
                  end_year: str,
                  author: str,
                  journal: str,
                  sorting: str) -> Dict:
        """format data to search format"""
        return {}

    @abstractmethod
    def getTotalPaperNum(self):
        """
        Get the total number of result
        Returns:
            num: number of search result
        """
        return

    @abstractmethod
    def getAllPapers(self, queue: PriorityQueue, num: int):
        """
        Get all papers detail
        Params:
            queue: a process queue for storing result and feedbacking progess,
                data format is [index, (title, authors, date, publication, abstract, doi, web)]
            num: number of papers to get
        """
        return
