from typing import List, TypeVar
from importlib import import_module
from getpaper.config import ROOT_DIR
from urllib import request as ur
from http import cookiejar


def getSpiderList() -> List[str]:
    return [spider.name.rstrip(".py") for spider in ROOT_DIR.glob("spiders/*.py") if not spider.name.startswith("_")] 

def getSpider(name: str):
    try:
        return getattr(import_module(f"getpaper.spiders.{name}"), f"{name}Spider")
    except ModuleNotFoundError:
        print(f"Not found spider '{name}' in spdiers folder")

def opener_creat():
    # 创建cookie
    cookie = cookiejar.CookieJar()
    cookie_handler = ur.HTTPCookieProcessor(cookie)
    http_handler = ur.HTTPHandler()
    https_handler = ur.HTTPSHandler()
    opener = ur.build_opener(cookie_handler, http_handler, https_handler)
    return opener