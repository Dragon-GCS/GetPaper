import asyncio
from queue import Queue
from typing import Dict

from bs4 import BeautifulSoup

from getpaper.spiders._spider import _Spider
from getpaper.utils import AsyncFunc, getSession


class Spider(_Spider):
    base_url = 'https://pubs.acs.org/action/doSearch'

    def parseData(self, keyword: str,
                  start_year: str,
                  end_year: str,
                  author: str,
                  journal: str,
                  sorting: str) -> Dict:
        data = {"AllField": keyword}
        return data

    @AsyncFunc
    async def getTotalPaperNum(self):
        """
        获取查找文献的总数
        """
        try:
            async with getSession() as session:
                html = await self.getHtml(session, self.data)
            bs = BeautifulSoup(html, 'lxml')
            total_num = bs.find("span", attrs = {'class': 'result__count'}).string  # type:ignore
            return f"共找到{total_num}篇"
        except asyncio.exceptions.TimeoutError:
            return "连接超时"

    @AsyncFunc
    async def getAllPapers(self, result_queue: Queue, num: int):
        num = result_queue.maxsize
        return super().getAllPapers(num)


if __name__ == '__main__':
    pass
