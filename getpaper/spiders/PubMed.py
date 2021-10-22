from multiprocessing import Queue
import re
from bs4 import BeautifulSoup
from typing import Dict
from getpaper.spiders._spider import _Spider
from getpaper.utils import AsyncFunc, getSession
import asyncio


class Spider(_Spider):
    base_url = "https://pubmed.ncbi.nlm.nih.gov/"

    def parseData(self, keyword: str, start_year: str, end_year: str, author: str, journal: str, sorting: str) -> Dict:
        data = {}
        term = [f"{keyword}"]
        # 处理搜索时间范围
        if start_year and end_year:
            term.append(f"{start_year}:{end_year}[dp]")
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
        """获取查找文献的总数"""
        try:
            async with getSession() as session:
                html = await self.getHtml(session, self.data)
            bs = BeautifulSoup(html, 'lxml')
            total_num = bs.find("div", attrs = {'class': 'results-amount'}).span.string.replace(",", "")  # type:ignore
        except AttributeError:
            total_num = "0"
        except asyncio.exceptions.TimeoutError:
            return "连接超时"
        return f"共找到{total_num}篇"

    async def getPagesInfo(self, page):
        self.data["page"] = str(page)
        data = self.data.copy()
        async with getSession() as session:
            html = await self.getHtml(session, self.data.copy())
        return self.parseHtml(data)

    def parseHtml(self, html):
        return html["page"]

    @AsyncFunc
    async def getAllpapers(self, result_queue:Queue, num:int):
        self.data.update({"size"  : "200",
                          "format": "pubmed"})
        tasks = []
        for page in range(num):
            self.data["page"] = str(page + 1)
            tasks.append(asyncio.create_task(self.getPagesInfo(page + 1)))
        return await asyncio.gather(*tasks)

    def test(self, q, num):
        import time
        for i in range(num):
            q.put(i)
            print("in spider:", q.qsize())
            time.sleep(1)

if __name__ == '__main__':
    q = Queue(5)
    pubmed = Spider("dna human")
    print(pubmed.getAllpapers(q, 5))
