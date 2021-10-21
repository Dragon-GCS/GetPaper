from typing import Dict
from aiohttp import ClientSession, CookieJar
from abc import ABC, abstractmethod


class _Spider(ABC):
    base_url: str

    def __init__(self, keyword: str,
                 start_year: str = None,
                 end_year: str = None,
                 author: str = None,
                 journal: str = None,
                 sorting: str = None) -> None:
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
        response = await session.get(self.base_url, params = params)
        return await response.text()

    @abstractmethod
    def parseData(self, keyword, start_year, end_year, author, journal, sorting) -> Dict:
        """format data to search format"""
        return {}

    @abstractmethod
    def getTotalPaperNum(self):
        """Get the total number of result"""
        pass

    @abstractmethod
    def getAllpapers(self, num: int):
        """Fetch paper detail"""
        pass
