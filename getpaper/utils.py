import asyncio

from aiohttp import ClientSession, CookieJar
from datetime import datetime
from functools import wraps
from importlib import import_module
from threading import Thread
from typing import Optional

from getpaper.config import HEADER, TIMEOUT


def getSpider(name: str, *args, **kwargs) -> Optional[object]:
    """
    Return a instance of spider by name
    :param name: spider's name, spider's class name is {name}Spider
    :return spider: an instance of specified by name
    """
    try:

        cls = getattr(import_module(f"getpaper.spiders.{name}"), "Spider")
        spider = cls.__new__(cls)
        spider.__init__(*args, **kwargs)
        return spider
    except ModuleNotFoundError as e:
        print(f"Import spider '{name}' Error")
        print(e)


def getTranslator(name: str, *args, **kwargs) -> Optional[object]:
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
    except ModuleNotFoundError as e:
        print(f"Import translator '{name}' Error")
        print(e)


def getNowYear() -> str:
    return str(datetime.now().year + 1)


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



def startThread(func):
    """
    An wrapped for start a new thread about spider in MainFrame
    """
    @wraps(func)
    def wrapped(self, *args, **kwargs) -> None:
        if not self.engine.get():
            self.tip.setTip("未选择搜索引擎")
        else:
            self.spider = getSpider(name = self.engine.get(),
                                    keyword = self.keyword.get(),
                                    start_year = self.start_year.get(),
                                    end_year = self.end_year.get(),
                                    author = self.author.get(),
                                    journal = self.journal.get(),
                                    sorting = self.sorting.get())
            t = Thread(target = func, args=(self, *args), kwargs=kwargs)
            t.setDaemon(True)
            t.start()
    return wrapped