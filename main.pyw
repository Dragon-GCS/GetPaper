import asyncio
import sys

# run below code to avoid RunTimeError raised on windows
if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())  # type: ignore

import logging


class ProjectFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        return record.name.lower().startswith("getpaper")


logger = logging.getLogger("GetPaper")
logger.setLevel(logging.INFO)

handler = logging.StreamHandler()
handler.setLevel(logging.INFO)
handler.addFilter(ProjectFilter())
handler.setFormatter(
    logging.Formatter(
        fmt="[%(asctime)s %(levelname)s] -"
        " %(filename)s[line:%(lineno)d] - Thread[%(threadName)s] - Task[%(taskName)s]\n"
        "%(message)s",
        datefmt="%H:%M:%S",
    )
)
logger.addHandler(handler)

from getpaper.GUI import Application

if __name__ == "__main__":
    app = Application("flatly")
    app.run()
