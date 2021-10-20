from typing import Dict
from aiohttp import ClientSession, CookieJar
from abc import ABC, abstractclassmethod
from getpaper.config import HEADER, TIMEOUT
from datetime import datetime

class _Spider(ABC):
    base_url: str
    def __init__(self, keyword:str, 
                    start_year:str = "1900", 
                      end_year:str = str(datetime.now().year + 1), 
                        author:str = None,
                       journal:str = None,
                        sorted:str = None,
                       reverse:int = 0) -> None:
        """
        Base spider
        Args:
            keyword: keyword, split by space
            start_year: default to 1900
            end_year: default to next year
            author: filter by author, default to None
            journal: filter by published journal, default to None
            sorted: sorted result by data or match 
        """
        self.data = self.parseData(keyword, start_year, end_year, author, journal, sorted, reverse)

    def getSession(self) -> ClientSession:
        """
        Create a async Http session by aiohttp
        """
        return ClientSession(headers=HEADER,
                             read_timeout=TIMEOUT,
                             cookie_jar=CookieJar(unsafe=True))


    async def getHtml(self, session:ClientSession, params:dict = {}) -> str:
        """Async get html"""
        response = await session.get(self.base_url, params=params)
        print("URL:", response.url)
        return await response.text()


    @abstractclassmethod
    def parseData(self, keyword, start_year, end_year, author, journal, sorted, reverse) -> Dict:
        """format data to search format"""
        return {}


    @abstractclassmethod
    def getTotalPaperNum(self):
        """Get the total number of result"""
        pass

    @abstractclassmethod
    def getAllpapers(self, num:int):
        """Fetch paper detail"""
        pass


