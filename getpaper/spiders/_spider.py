from abc import ABC, abstractmethod
from queue import PriorityQueue
from typing import Any

from aiohttp import ClientSession


class _Spider(ABC):
    base_url: str
    total_num: int
    session: ClientSession
    result_queue: PriorityQueue

    def __init__(
        self,
        keyword: str = "",
        start_year: str = "",
        end_year: str = "",
        author: str = "",
        journal: str = "",
        sorting: str = "",
    ) -> None:
        """Base spider

        Args:
            keyword: keyword, split by space
            start_year: default to 1900
            end_year: default to next year
            author: filter by author, default to None
            journal: filter by published journal, default to None
            sorting: sorting result by details or match
        """
        self.data = self.parseData(keyword, start_year, end_year, author, journal, sorting)

    @abstractmethod
    def parseData(
        self, keyword: str, start_year: str, end_year: str, author: str, journal: str, sorting: str
    ) -> dict[str, Any]:
        """format details to search format"""
        return {}

    @abstractmethod
    def getTotalPaperNum(self) -> str:
        """Get the total number of result

        Returns:
            num: number of search result
        """
        pass

    @abstractmethod
    def getAllPapers(
        self, queue: PriorityQueue[tuple[int, tuple[str, str, str, str, str, str, str]]], num: int
    ):
        """Get all papers detail

        Args:
            queue: a priority queue for storing result and was monitored by GUI thread then feedback progress,
                details format is [index, (title, authors, date, publication, abstract, doi, web)]
            num: number of papers to get
        """
        pass
