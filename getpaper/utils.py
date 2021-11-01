import asyncio
import logging
import sys
from datetime import datetime
from functools import wraps
from importlib import import_module
from queue import PriorityQueue
from threading import Thread
from typing import Any, Callable, List, Optional

from aiohttp import ClientSession, CookieJar

from getpaper.config import HEADER, TIMEOUT

log = logging.getLogger("GetPaper")

def getSpider(name: str, *args, **kwargs) -> Optional[object]:
    """
    Create a Spider by name
    :param name: spider's name, spider's class name is {name}Spider
    :return spider: an instance of specified by name
    """
    cls = getattr(import_module(f"getpaper.spiders.{name}"), "Spider")
    return cls(*args, **kwargs)


def getTranslator(name: str, *args, **kwargs) -> Optional[object]:
    """
    Create a Translator by name
    :param name: translator's name, translator's class name is Translator
    :return translator: an instance of specified by name
    """
    cls = getattr(import_module(f"getpaper.translator.{name}"), "Translator")
    return cls(*args, **kwargs)


def getNowYear() -> str:
    """Get the year of now"""
    return str(datetime.now().year + 1)


def getSession() -> ClientSession:
    """Create a async Http session by aiohttp"""
    return ClientSession(headers = HEADER,
                         read_timeout = TIMEOUT,
                         cookie_jar = CookieJar(unsafe = True))


def AsyncFunc(func: Callable[..., Any]):
    """A decorator for running the async function as a common function"""

    @wraps(func)
    def wrapped(*args, **kwargs):
        # run below code to avoid RunTimeError raised by aiohttp's on windows
        if sys.platform.startswith("win"):
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        return asyncio.run(func(*args, **kwargs))

    return wrapped


def startThread(thread_name: str = ""):
    """A decorator for running app function in new thread, name for debug"""

    def middle(func: Callable[..., Any]):
        @wraps(func)
        def wrapped(self, *args, **kwargs) -> None:
            MyThread(tip_set = self.tip.setTip,
                     target = func,
                     args = (self, *args),
                     kwargs = kwargs,
                     daemon = True,
                     name = thread_name).start()

        return wrapped

    return middle


def checkSpider(func: Callable[..., Any]):
    """A decorator for check whether choose spider"""

    @wraps(func)
    def wrapped(self, *args, **kwargs) -> None:
        if not self.engine.get():
            self.tip.setTip("未选择搜索引擎")
            return
        else:
            self.spider = getSpider(name = self.engine.get(),
                                    keyword = self.keyword.get(),
                                    start_year = self.start_year.get(),
                                    end_year = self.end_year.get(),
                                    author = self.author.get(),
                                    journal = self.journal.get(),
                                    sorting = self.sorting.get())
        func(self, *args, **kwargs)

    return wrapped


def getQueueData(queue: PriorityQueue) -> List[str]:
    """
    Sort details in queue by item[0]
    Args:
        queue: result queue
    Returns:
        returns: list of sorted details in queue
    """
    result = []
    while not queue.empty():
        result.append(queue.get()[1])
    return result


class MyThread(Thread):
    def __init__(self, tip_set: Callable[..., Any], **kwargs) -> None:
        super().__init__(**kwargs)
        self.tip_set = tip_set

    def run(self) -> None:
        """Overwrite self.run() for catching the TipException and show on Tipbar"""
        try:
            self.result = self._target(*self._args, **self._kwargs) \
                if self._target else None
        except TipException as t:
            self.tip_set(t.tip)
        except Exception as e:
            log.error(e)
            self.tip_set("未知错误")
        finally:
            del self._target, self._args, self._kwargs


class TipException(Exception):
    def __init__(self, tip, *args: object) -> None:
        super().__init__(*args)
        self.tip = tip
