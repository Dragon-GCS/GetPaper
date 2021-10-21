from asyncio import tasks
from datetime import time
import re
from bs4 import BeautifulSoup
from multiprocessing.context import Process
from typing import Dict
from getpaper.spiders._spider import _Spider
from getpaper.utils import AsyncFunc, getSession
import asyncio


class Spider(_Spider):
    base_url = "https://pubmed.ncbi.nlm.nih.gov/"

    def parseData(self, keyword: str,
                  start_year: str,
                  end_year: str,
                  author: str,
                  journal: str,
                  sorting: str) -> Dict:
        data = {}
        # 处理搜索关键字以及搜索时间范围
        term = [f"{keyword}", f"{start_year}:{end_year}[dp]"]
        # 指定搜索作者
        if author:
            term.append(f"{author}[author]")
            # 指定搜索期刊
        if journal:
            term.append(f"{journal}[journal]")
        data["term"] = " AND ".join(term)
        if sorting.startswith("日期"):
            data["sort"] = "date"
        if sorting.endswith("逆序"):
            data["sort_order"] = "asc"
        return data

    @AsyncFunc
    async def getTotalPaperNum(self):
        """
        获取查找文献的总数
        """
        async with getSession() as session:
            html = await self.getHtml(session, self.data)
        bs = BeautifulSoup(html, 'lxml')
        try:
            total_num = bs.find("div", attrs = {'class': 'results-amount'}).span.string  # type:ignore
        except AttributeError:
            total_num = "0"
        return total_num.replace(",", "")  # type:ignore

    async def getPagesInfo(self, page):
        self.data["page"] = str(page)
        data = self.data.copy()
        async with getSession() as session:
            html = await self.getHtml(session, self.data.copy())
        return self.parseHtml(data)

    def parseHtml(self, html):
        return html["page"]

    @AsyncFunc
    async def getAllpapers(self, num: int):
        self.data.update({"size"  : "200",
                          "format": "pubmed"})
        tasks = []
        for page in range(num):
            self.data["page"] = str(page + 1)
            tasks.append(asyncio.create_task(self.getPagesInfo(page + 1)))
        return await asyncio.gather(*tasks)


if __name__ == '__main__':
    pubmed = Spider("dna human")
    print(pubmed.getAllpapers(5))
