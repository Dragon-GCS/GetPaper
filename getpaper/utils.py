import logging
from asyncio import iscoroutine, run_coroutine_threadsafe
from concurrent.futures import Future
from datetime import datetime
from functools import cache, wraps
from importlib import import_module
from queue import PriorityQueue
from threading import Thread
from typing import Any, Callable, ParamSpec

from curl_cffi.requests import AsyncSession

from getpaper.config import CLIENT_TIMEOUT, LOOP
from getpaper.spiders._spider import _Spider
from getpaper.translator._translator import _Translator

log = logging.getLogger("GetPaper")


def getSpider(name: str, *args, **kwargs) -> _Spider:
    """Return a Spider by name

    Args:
        name: Spider's filename, should be found in getpaper/spiders
    Returns:
        spider: An instance of specified by name
    """

    cls = import_module(f"getpaper.spiders.{name}").Spider
    return cls(*args, **kwargs)


def getTranslator(name: str, *args, **kwargs) -> _Translator:
    """Create a Translator by name

    Args:
        name: Translator's filename, should be found in getpaper/translator
    Returns:
        translator: An instance of specified by name
    """

    cls = import_module(f"getpaper.translator.{name}").Translator
    return cls(*args, **kwargs)


def getNowYear() -> str:
    """Get the year of now"""

    return str(datetime.now().year + 1)


@cache
def getClient() -> AsyncSession:
    """Create a async Http session by curl_cffi AsyncSession"""
    return AsyncSession(impersonate="chrome", timeout=CLIENT_TIMEOUT)


P = ParamSpec("P")


def startTask[T](
    task_name: str = "",
):
    """A decorator for running async function in a loop thread, name for debug"""

    def middle(func: Callable[P, T]) -> Callable[P, Future[T]]:
        @wraps(func)
        def wrapped(*args: P.args, **kwargs: P.kwargs) -> Future[T]:
            async def task() -> T:
                result = func(*args, **kwargs)
                if iscoroutine(result):
                    return await result
                return result

            async def create_task() -> T:
                return await LOOP.create_task(task(), name=task_name)

            return run_coroutine_threadsafe(create_task(), LOOP)

        return wrapped

    return middle


def setSpider(func: Callable[..., Any]) -> Callable[..., None]:
    """A decorator for check whether choose spider"""

    @wraps(func)
    def wrapped(self, *args, **kwargs) -> None:
        if not self.engine.get():
            self.tip.setTip("未选择搜索引擎")
            return
        self.spider = getSpider(
            name=self.engine.get(),
            keyword=self.keyword.get(),
            start_year=self.start_year.get(),
            end_year=self.end_year.get(),
            author=self.author.get(),
            journal=self.journal.get(),
            sorting=self.sorting.get(),
        )
        log.info(f"Init this spider: {self.engine.get()}")
        func(self, *args, **kwargs)

    return wrapped


def getQueueData(queue: PriorityQueue) -> list[list[str]]:
    """Extract data from queue

    Args:
        queue: result queue
    Returns:
        returns: list of data in queue
    """
    result = []
    while not queue.empty():
        _index, data = queue.get()
        result.append(data)
    return result


class MyThread(Thread):
    _target: Callable
    _args: tuple
    _kwargs: dict

    def __init__(self, tip_set: Callable[..., Any], **kwargs) -> None:
        """An thread that can catch the exception in the target and display on GUI, save returns of target.

        Args:
            tip_set: A function to display tip on GUI
        """
        super().__init__(**kwargs)
        self.tip_set = tip_set
        self.result = None

    def run(self) -> None:
        """Overwrite self.run() for catching the TipException and show on TipBar"""

        try:
            self.result = self._target(*self._args, **self._kwargs) if self._target else None
        except TipException as t:
            self.tip_set(t.tip)
        except Exception:
            log.exception("Thread unknown error")
            self.tip_set("未知错误")
        finally:
            del self._target, self._args, self._kwargs


class TipException(Exception):
    def __init__(self, tip, *args: object) -> None:
        super().__init__(*args)
        self.tip = tip
