import asyncio
import datetime
from functools import wraps
from typing import List, Optional
from importlib import import_module
from getpaper.config import ROOT_DIR, HEADER, TIMEOUT
from aiohttp import ClientSession, CookieJar


def getSpiderList() -> List[str]:
    """Spider.py which in getpaper/spiders will be find and show in GUI"""
    return [spider.name.rstrip(".py") for spider in ROOT_DIR.glob("spiders/*.py") if not spider.name.startswith("_")] 


def getSpider(name: str, *args, **kwargs) -> Optional:
    """
    Return a instance of spider by name
    :param name: spider's name, spider's class name is {name}Spider
    :return spider: an instance of specified by name
    """
    try:
        cls = getattr(import_module(f"getpaper.spiders.{name}"), f"{name}Spider")
        spider = cls.__new__(cls)
        spider.__init__(*args, **kwargs)
        return spider
    except ModuleNotFoundError:
        print(f"Not found spider '{name}' in spdiers folder")


def getTranslatorList() -> List[str]:
    return [translator.name.rstrip(".py") for translator in ROOT_DIR.glob("translator/*.py") if not translator.name.startswith("_")]


def getTranslator(name: str, *args, **kwargs) -> Optional:
    """
    Return a instance of translator by name
    :param name: translator's name, translator's class name is Translator
    :return translator: an instance of specified by name
    """
    try:
        cls = getattr(import_module(f"getpaper.translator.{name}"), "Translator")
        translator = cls.__new__(cls)
        translator.__init__(*args, **kwargs)
        return translator
    except ModuleNotFoundError:
        print(f"Not found translator '{name}' in translator folder")


def getNowYear() -> str:
    return str(datetime.datetime.now().year + 1)


def getSession() -> ClientSession:
    """Create a async Http session by aiohttp"""
    return ClientSession(headers = HEADER,
                         read_timeout = TIMEOUT,
                         cookie_jar = CookieJar(unsafe = True))


def AsyncFunc(func):
    """
    An wrapped for run the async function as a common function
    """
    @wraps(func)
    def wrapped(*args, **kwargs):
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(func(*args, **kwargs))
    return wrapped
