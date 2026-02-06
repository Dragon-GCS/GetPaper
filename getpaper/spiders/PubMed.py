import asyncio
import logging
import re
from queue import PriorityQueue
from typing import Any, Dict, Sequence

from bs4 import BeautifulSoup
from curl_cffi.requests.exceptions import Timeout

from getpaper.spiders._spider import _Spider
from getpaper.utils import TipException, getClient

GET_FREQUENCY = 0.1  # frequency to fetch paper
log = logging.getLogger("GetPaper")


class Spider(_Spider):
    base_url = "https://pubmed.ncbi.nlm.nih.gov/"
    single_page_pmid: str

    def parseData(
        self,
        keyword: str,
        start_year: str = "",
        end_year: str = "",
        author: str = "",
        journal: str = "",
        sorting: str = "",
    ) -> Dict[str, Any]:
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
        self.data = data
        return data

    async def getTotalPaperNum(self) -> int:
        self.data["format"] = "summary"
        client = getClient()
        try:
            resp = await client.get(self.base_url, params=self.data)
            log.info(f"Get URL: {resp.url}\nURL Status: {resp.status_code}")
            bs = BeautifulSoup(resp.text, "lxml")
            if bs.find("span", class_="single-result-redirect-message"):
                self.total_num = 1
                if pmid := bs.find("strong", class_="current-id"):
                    self.single_page_pmid = pmid.text
                else:
                    self.single_page_pmid = ""
            elif tag := bs.find("div", class_="results-amount"):
                self.total_num = int(tag.span.text.replace(",", ""))  # type: ignore
            else:
                self.total_num = 0
        except Timeout as e:
            log.exception("PubMed Spider Get Total Num Time Out")
            raise TipException("连接超时") from e

        return self.total_num

    async def getPMIDs(self, num: int) -> Sequence[str]:
        """
        Get the paper's PMIDs
        Args:
            num: Number of PMIDs to fetch
        """
        pmid_list = []
        self.data.update({"size": "200", "page": 1, "format": "pmid"})
        client = getClient()
        # Get page by order and fetch PMIDs
        try:
            while self.data["page"] <= (num - 1) // 200 + 1:
                resp = await client.get(self.base_url, params=self.data.copy())
                log.info(f"Get URL: {resp.url}\nURL Status: {resp.status_code}")
                bs = BeautifulSoup(resp.text, "lxml")
                # If no pmid was find, modify result.max_size to 1 for stop monitoring.
                if not (tag := bs.find("pre", class_="search-results-chunk")):
                    self.result_queue.maxsize = 1
                    self.result_queue.put((0, ["Not found any papers"] * 7))
                    raise TipException("未找到相关文献")  # noqa: TRY301

                result = tag.text.split()
                pmid_list.extend(result)
                # Stop if find only one pmid
                if len(result) == 1:
                    break

                self.data["page"] += 1
        except asyncio.exceptions.TimeoutError as e:
            log.info("PubMed Fetch PMIDs Time Out")
            raise TipException("连接超时") from e
        except Exception:
            log.exception(f"PubMed Error in fetching PMIDs[{self.data['page']} / {num // 200 + 1}]")
        return pmid_list[:num]

    async def getPagesInfo(self, index: int, pmid: str):
        title = "No Title"
        authors = "No Author"
        doi = "No DOI"
        publication = "No Publication"
        abstract = "No Abstract"
        date = "No Date"
        web = self.base_url + pmid

        client = getClient()
        # Decrease access frequency
        await asyncio.sleep(index * GET_FREQUENCY)
        log.debug(f"Fetching PMID[{pmid}]")

        try:
            res = await client.get(web)
            bs = BeautifulSoup(res.text, "lxml")
        except Exception:
            log.exception(f"PMID[{pmid}] Spider Error")
            title, authors, date, publication, abstract, doi = ["Error"] * 6
        else:
            content = bs.find("main", class_="article-details")
            if not content:
                return

            if tag := content.find("h1", class_="heading-title"):
                title = re.sub(r"\s{2,}", "", tag.text)

            if tag := content.find("span", class_="cit"):
                date = tag.text

            if tag := content.find("button", id="full-view-journal-trigger"):
                publication = re.sub(r"\s+", "", tag.text)

            if authors := content.find_all("span", class_="authors-list-item", limit=5):
                authors = "; ".join([a.text for author in authors if (a := author.find("a"))])

            if tag := content.find(class_="abstract-content selected"):
                abstract = re.sub(r"\s{2,}", "", tag.text)

            if tag := content.find("a", attrs={"data-ga-action": "DOI"}):
                doi = re.sub(r"\s+", "", tag.text)

            if link := content.find(class_="full-text-links-list"):
                web = link.a["href"]  # type: ignore
        finally:
            self.result_queue.put((index, (title, authors, date, publication, abstract, doi, web)))

    async def getAllPapers(self, queue: PriorityQueue, num: int) -> None:
        self.result_queue = queue
        num = max(num, 1)

        tasks = []
        if self.total_num == 1 and hasattr(self, "single_page_pmid"):
            tasks = [self.getPagesInfo(0, self.single_page_pmid)]
        else:
            PMIDs = await self.getPMIDs(num)
            tasks = [self.getPagesInfo(index, pmid) for index, pmid in enumerate(PMIDs)]

        await asyncio.gather(*tasks)


if __name__ == "__main__":
    pubMed = Spider(
        keyword="dna",
        start_year="2010",
        end_year="2020",
        author="Martin",
        journal="nature",
        sorting="相关性",
    )

    print(pubMed.getTotalPaperNum())
    q = PriorityQueue(1)
    asyncio.run(pubMed.getAllPapers(q, 1))
    for _ in range(1):
        print(q.get())
