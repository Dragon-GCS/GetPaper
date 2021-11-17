import asyncio
import logging
from queue import PriorityQueue
import re
from typing import Any, Dict

from bs4 import BeautifulSoup

from getpaper.spiders._spider import _Spider
from getpaper.utils import AsyncFunc, getSession, TipException

GET_FREQUENCY = 0.05
log = logging.getLogger("GetPaper")

class Spider(_Spider):
    base_url = 'https://pubs.acs.org/action/doSearch'

    def parseData(self, keyword: str,
                  start_year: str = "",
                  end_year: str = "",
                  author: str = "",
                  journal: str = "",
                  sorting: str = "") -> Dict[str, Any]:
        data = {"AllField": keyword,
                "startPage": 0}
        # Parsing author field
        if author:
            data["Contrib"] = author
        # Paring search time range field
        if start_year:
            data["BeforeYear"] = start_year
        if end_year:
            data["AfterYear"] = end_year
        # Journal/publication need to be selected from the range specified by ACS, so pass
        # Parsing result sort order
        if sorting.startswith("日期"):
            data["sortBy"] = "Earliest"
        if sorting.endswith("逆序"):
            data["sortBy"] = "Earliest_asc"

        return data

    @AsyncFunc
    async def getTotalPaperNum(self):
        self.data["startPage"] = 0
        self.data["pageSize"] = 20
        try:
            async with getSession() as session:
                async with session.get(self.base_url, params = self.data) as response:
                    log.info(f"Get URL: {response.url}\nURL Status: {response.status}")
                    html = await response.text()
        except asyncio.exceptions.TimeoutError:
            log.info("ACS Spider Get Total Num Time Out")
            raise TipException("连接超时")
        else:
            bs = BeautifulSoup(html, 'lxml')
            total_num = bs.find("span", attrs = {'class': 'result__count'}).string  # type:ignore
            return f"共找到{total_num}篇"


    async def getPagesInfo(self, data: Dict[str, Any], num: int) -> None:
        """
        Get paper's detail on a html
        Args:
            data: search data for getting html
            num: The number of papers to be fetched on a html
        """
        page = data["startPage"]
        # Decrease access frequency
        await asyncio.sleep(page * GET_FREQUENCY)

        try:
            async with self.session.get(self.base_url, params = data) as response:
                log.info(f"Get URL: {response.url}\nURL Status: {response.status}")
                html = await response.text()
        except Exception as e:
            log.error(f"ACS Spider Error: {e}")
            for index in range(page * 100, min((page + 1) * 100, num)):
                self.result_queue.put((index, ["Error"] * 6))
        else:
            bs = BeautifulSoup(html, 'lxml')
            contents = iter(bs.find_all(class_ = "issue-item_metadata"))
            for index in range(page * 100, min((page + 1) * 100, num)):
                content = (next(contents))
                # Find titles、doi、web_url
                title_tag = content.find("h2", class_ = "issue-item_title")
                title = title_tag.text if title_tag else "No title"
                doi = title_tag.a["href"].lstrip("/doi/") if title_tag else "No DOI"
                web = 'https://pubs.acs.org' + title_tag.a["href"] if title_tag else "No URL"
                # Find authors list
                authors = tag.text \
                        if (tag := content.ul) \
                        else "No Authors"
                # Find publish date
                date = tag.text \
                    if (tag := content.find(class_ = 'pub-date-value')) \
                    else "No Publicate Date"
                # Find abstracts
                abstract = tag.text \
                        if (tag := content.find("span", class_ = 'hlFld-Abstract')) \
                        else "No Abstract"

                # find publications
                # Chapter and article have different format
                if content.parent.find(class_ = 'infoType').string == 'Chapter':
                    publication = re.sub(r'\s+', ' ', content.find(class_ ='issue-item_chapter').text)
                else:
                    publication = tag.text \
                                if (tag := content.find(class_ = 'issue-item_jour-name')) \
                                else "No Publication"
                # Save data to result queue
                self.result_queue.put((index,
                                    (title, authors, date, publication, abstract, doi, web)))

    @AsyncFunc
    async def getAllPapers(self, result_queue: PriorityQueue, num: int) -> None:
        self.result_queue = result_queue
        num = max(1, num)
        self.data["pageSize"] = 100

        if getattr(self, "session", None) is None:
            self.session = getSession()

        tasks = []
        for page in range((num - 1) // 100 + 1):
            self.data["startPage"] = page
            tasks.append(self.getPagesInfo(self.data.copy(), num))

        await asyncio.gather(*tasks)

        if hasattr(self, "session"):
            try:
                await self.session.close()
            finally:
                del self.session


if __name__ == '__main__':
    acs = Spider(keyword = "human",
                start_year = "2010",
                end_year = "2020",
                author = "Martin",
                journal = "nature",
                sorting = "日期逆序"
                )
    print(acs.getTotalPaperNum())
    q = PriorityQueue(4)
    acs.getAllPapers(q, 4)
    for i in range(4):
        print(q.get())
