import asyncio
import time
from multiprocessing import Queue
from typing import Dict

from bs4 import BeautifulSoup

from getpaper.spiders._spider import _Spider
from getpaper.utils import AsyncFunc, getSession


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

    async def getPagesInfo(self, session, data):
        html = await self.getHtml(session, data)
        time.sleep(1)
        self.result_queue.put((data["page"], list(data.values())))
        return self.parseHtml(data)

    def parseHtml(self, html):
        return html["page"]

    @AsyncFunc
    async def getAllPapers(self, result_queue: Queue, num: int):
        self.data.update({"size"  : "200",
                          "format": "pubmed"})
        pages = num // 200 + 1
        self.result_queue = result_queue
        tasks = []
        async with getSession() as session:
            for page in range(1, num + 1):
                self.data["page"] = str(page)
                tasks.append(self.getPagesInfo(session, self.data.copy()))
            result = await asyncio.gather(*tasks)
        return result

    def test(self, q, num):
        import time
        for i in range(num):
            q.put(i)
            print("in spider:", q.qsize())
            time.sleep(1)


if __name__ == '__main__':
    q = Queue(5)
    pubmed = Spider("dna human")
    print(pubmed.getAllPapers(q, 5))
