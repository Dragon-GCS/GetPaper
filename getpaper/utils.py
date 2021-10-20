import asyncio
from multiprocessing import Process
from functools import wraps
from typing import Callable, List, TypeVar, Optional
from importlib import import_module
from getpaper.config import ROOT_DIR
from getpaper.spiders._spider import _Spider
from urllib import request as ur
from http import cookiejar


def getSpiderList() -> List[str]:
    return [spider.name.rstrip(".py") for spider in ROOT_DIR.glob("spiders/*.py") if not spider.name.startswith("_")] 

def getSpider(name: str) -> Optional["_Spider"]:
    try:
        return getattr(import_module(f"getpaper.spiders.{name}"), f"{name}Spider")
    except ModuleNotFoundError:
        print(f"Not found spider '{name}' in spdiers folder")

def AsyncFunc(func):
    """
    An wrapped for run the async function as a common function
    """
    @wraps(func)
    def wraped(*args, **kwargs):
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(func(*args, **kwargs))
    return wraped