import asyncio
import importlib.resources
import json
import logging
from hashlib import md5
from random import randint
from typing import Any

from getpaper.translator._translator import _Translator
from getpaper.utils import AsyncFunc, TipException, getSession

log = logging.getLogger("GetPaper")


def make_md5(s, encoding="utf-8"):
    return md5(s.encode(encoding)).hexdigest()


class Translator(_Translator):
    url = "https://fanyi-api.baidu.com/api/trans/vip/translate"
    key: str = ""
    appid: str = ""
    data: dict

    def __init__(self) -> None:
        try:
            info = json.loads(
                importlib.resources.read_text("getpaper.translator", "_api_info.json")
            )
        except FileNotFoundError as e:
            log.exception("未找到密钥文件")
            raise TipException("未找到密钥文件") from e
        else:
            self.key = info["百度翻译"]["key"]
            self.appid = info["百度翻译"]["appid"]
        self.salt = str(randint(32768, 65536))
        self.data = {
            "appid": self.appid,
            "q": "",
            "from": "auto",
            "to": "zh",
            "salt": self.salt,
            "sign": "",
        }

    def sign_query(self, query: str) -> dict[str, Any]:
        """
        Preprocess translation query

        Args:
            query: String to translate
        Returns:
            data: A dict storing translation string and processed sign.
        """
        sign = self.appid + query + self.salt + self.key
        self.data["sign"] = make_md5(sign)
        self.data["q"] = query
        return self.data

    @AsyncFunc
    async def translate(self, detail: str) -> str:
        async with getSession() as session:
            while True:
                params = self.sign_query(detail)
                try:
                    response = await session.post(self.url, params=params)
                    result = await response.json()
                except Exception as e:
                    log.exception("翻译失败")
                    raise TipException("翻译失败") from e
                if result.get("error_code") == "54003":
                    await asyncio.sleep(1)
                elif result.get("error_code") == "52003":
                    return "Api密钥无效"
                else:
                    break
        return "\n".join([item["dst"] for item in result["trans_result"]])


if __name__ == "__main__":
    trans = Translator()
    print(trans.translate("Test\nstring second \nstring"))
