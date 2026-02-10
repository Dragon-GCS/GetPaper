import logging
from asyncio import iscoroutine, run_coroutine_threadsafe
from concurrent.futures import Future
from functools import cache, wraps
from importlib import import_module
from queue import PriorityQueue
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


class TipException(Exception):
    def __init__(self, tip, *args: object) -> None:
        super().__init__(*args)
        self.tip = tip
