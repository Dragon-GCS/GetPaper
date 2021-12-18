import asyncio
import logging
import re
from queue import PriorityQueue
from typing import Any, Dict, Sequence

from bs4 import BeautifulSoup

from getpaper.spiders._spider import _Spider
from getpaper.utils import AsyncFunc, TipException, getSession

GET_FREQUENCY = 0.1  # frequency to fetch paper
log = logging.getLogger("GetPaper")


class Spider(_Spider):
    base_url = "https://pubmed.ncbi.nlm.nih.gov/"
    single_page_pmid: str

    def parseData(self, keyword: str,
                  start_year: str = "",
                  end_year: str = "",
                  author: str = "",
                  journal: str = "",
                  sorting: str = "") -> Dict[str, Any]:
        """parse input parameters as url data"""
        data = {}
        # Parsing term field
        # Add keyword to term
        term = [f"{keyword}"]
        # Add search time range to term
        if start_year and end_year:
            term.append(f"{start_year}:{end_year}[dp]")
        # Add authors to term
        if author:
            term.append(f"{author}[author]")
        # Add publications to term
        if journal:
            term.append(f"{journal}[journal]")
        data["term"] = " AND ".join(term)

        # Parsing result sort order
        if sorting.startswith("日期"):
            data["sort"] = "date"
        if sorting.endswith("逆序"):
            data["sort_order"] = "asc"
        return data

    @AsyncFunc
    async def getTotalPaperNum(self):
        self.data["format"] = "summary"
        try:
            async with getSession() as session:
                async with session.get(self.base_url, params=self.data) as response:
                    log.info(
                        f"Get URL: {response.url}\nURL Status: {response.status}")
                    html = await response.text()
        except asyncio.exceptions.TimeoutError:
            log.info("PubMed Spider Get Total Num Time Out")
            raise TipException("连接超时")
        else:
            bs = BeautifulSoup(html, "lxml")
            if bs.find("span", class_="single-result-redirect-message"):
                self.total_num = 1
                self.single_page_pmid = bs.find("strong", class_ = "current-id").text
            else:
                total_num = int(tag.text.replace(",", "")) \
                    if (tag := bs.find("div", class_="results-amount").span) \
                    else 0
            return f"共找到{self.total_num}篇"

    async def getPMIDs(self, num: int) -> Sequence[str]:
        """
        Get the paper's PMIDs
        Args:
            num: Number of PMIDs to fetch
        """
        pmid_list = []
        self.data.update({"size": "200",
                          "page": 1,
                          "format": "pmid"})
        # Get page by order and fetch PMIDs
        try:
            while self.data["page"] <= (num - 1) // 200 + 1:
                async with self.session.get(self.base_url, params=self.data.copy()) as response:
                    log.info(
                        f"Get URL: {response.url}\nURL Status: {response.status}")
                    html = await response.text()

                bs = BeautifulSoup(html, "lxml")
                # If no pmid was find, modify result.max_size to 1 for stop monitoring.
                if not (tag := bs.find("pre", class_="search-results-chunk")):
                    self.result_queue.maxsize = 1
                    self.result_queue.put((0, ["Not found any papers"] * 7))
                    raise TipException("未找到相关文献")

                result = tag.text.split()
                pmid_list.extend(result)
                # Stop if find only one pmid
                if len(result) == 1:
                    break

                self.data["page"] += 1
        except asyncio.exceptions.TimeoutError:
            log.info("PubMed Fetch PMIDs Time Out")
            raise TipException("连接超时")
        except Exception as e:
            log.error(
                f"PubMed Erro in fetching PMIDs[{self.data['page']} / { num // 200 + 1}]: {e}")
        finally:
            return pmid_list[:num]

    async def getPagesInfo(self, index: int, pmid: str):
        web = self.base_url + pmid
        # Decrease access frequency
        await asyncio.sleep(index * GET_FREQUENCY)
        log.debug(f"Fetching PMID[{pmid}]")
        try:
            async with self.session.get(web) as html:
                bs = BeautifulSoup(await html.text(), "lxml")
        except Exception as e:
            log.error(f"PMID[{pmid}] Spider Error: {e}")
            title, authors, date, publication, abstract, doi = ["Error"] * 6
        else:
            content = bs.find("main", class_="article-details")

            title = re.sub(r"\s{2,}", "", tag.text) \
                if (tag := content.find("h1", class_="heading-title")) \
                else "No Title"

            date = tag.text \
                if (tag := content.find("span", class_="cit")) \
                else "No date"

            publication = re.sub(r"\s+", "", tag.text) \
                if (tag := content.find("button", id="full-view-journal-trigger")) \
                else "No publication"

            authors = "; ".join({author.a.text
                                 for author in content.find_all("span", class_="authors-list-item", limit=5)
                                 if author.find("a")})

            abstract = re.sub(r"\s{2,}", "", tag.text) \
                if (tag := content.find(class_="abstract-content selected")) \
                else "No Abstract"

            doi = re.sub(r"\s+", "", tag.text) \
                if (tag := content.find("a", attrs={"data-ga-action": "DOI"})) \
                else ""

            if tag := content.find(class_="full-text-links-list"):
                web = tag.a["href"]
        finally:
            self.result_queue.put((index,
                                   (title, authors, date, publication, abstract, doi, web)))

    @AsyncFunc
    async def getAllPapers(self, result_queue: PriorityQueue, num: int) -> None:
        self.result_queue = result_queue
        num = max(num, 1)

        if getattr(self, "session", None) is None:
            self.session = getSession()

        tasks = []

        if self.total_num == 1:
            tasks.append(self.getPagesInfo(0, self.single_page_pmid))
        else:
            for index, pmid in enumerate(await self.getPMIDs(num)):
                tasks.append(self.getPagesInfo(index, pmid))

        await asyncio.gather(*tasks)

        if hasattr(self, "session"):
            try:
                await self.session.close()
            finally:
                del self.session


if __name__ == "__main__":
    pubmed = Spider(keyword="crispr",
                    start_year="2010",
                    end_year="2020",
                    author="Martin",
                    journal="nature",
                    sorting="相关性"
                    )

    print(pubmed.getTotalPaperNum())
    q = PriorityQueue(1)
    pubmed.getAllPapers(q, 1)
    for i in range(1):
        print(q.get())
