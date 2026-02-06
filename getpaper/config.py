import asyncio
import sys
from pathlib import Path

if hasattr(sys, "frozen"):
    # add new module name without .py when using pyinstaller
    spider_list = ["ACS", "PubMed"]
    translator_list = ["百度翻译"]
else:
    spider_list = [
        spider.name.rstrip(".py")
        for spider in Path(__file__).parent.joinpath("spiders").iterdir()
        if not spider.name.startswith("_")
    ]
    translator_list = [
        translator.name.rstrip(".py")
        for translator in Path(__file__).parent.joinpath("translator").iterdir()
        if not translator.name.startswith("_")
    ]

spider_list.remove("ACS")


CLIENT_TIMEOUT = 10  # Global AsyncClient timeout
TIP_REFRESH = 0.2  # MainFrame's tip bar refresh frequency
SCI_DELAY = 0.1  # add delay avoid putting too much pressure on the Sci_Hub server

APP_NAME = "GetPaper"
DEFAULT_SCI_HUB_URL = "wellesu.com"
FRAME_STYLE = {"relief": "ridge", "padding": 10}
FONT = ("微软雅黑", 12)
SORTED_BY = ("相关性", "日期", "日期逆序")

# For Detail_Frame to show result detail
# fmt: off
RESULT_LIST_EN = ["Title:\n", "Authors:\n", "Date:\t", "Publication:\t", "Abstract:\n", "doi:\t", "Url:\t"]
RESULT_LIST_CN = ["标题:\n", "作者:\n", "日期:\t", "期刊:\t", "摘要:\n", "doi:\t", "网址:\t"]
# fmt: on

LOOP = asyncio.get_event_loop()

PROJECT_URL = "https://github.com/Dragon-GCS/GetPaper"
