import json
import time
from hashlib import md5
from random import randint
from typing import Dict

from getpaper.config import ROOT_DIR
from getpaper.utils import AsyncFunc, TipException, getSession


def make_md5(s, encoding = 'utf-8'):
    return md5(s.encode(encoding)).hexdigest()


class Translator:
    url = "https://fanyi-api.baidu.com/api/trans/vip/translate"
    key: str = ""
    appid: str = ""
    data: Dict = {}

    def __init__(self) -> None:
        try:
            with open(ROOT_DIR.joinpath("api_info.json"), encoding = "utf8") as f:
                info = json.load(f)
        except FileNotFoundError:
            raise TipException("未找到密钥文件")
        else:
            self.key = info["百度翻译"]["key"]
            self.appid = info["百度翻译"]["appid"]
        self.salt = str(randint(32768, 65536))
        self.data = {
                'appid': self.appid,
                'q'    : "",
                'from' : "auto",
                'to'   : "zh",
                'salt' : self.salt,
                'sign' : ""
        }

    def process(self, query: str) -> Dict:
        sign = self.appid + query + self.salt + self.key
        self.data["sign"] = make_md5(sign)
        self.data["q"] = query
        return self.data

    @AsyncFunc
    async def translate(self, detail: str) -> str:
        async with getSession() as session:
            while True:
                data = self.process(detail)
                try:
                    response = await session.post(self.url, params = data)
                    result = await response.json()
                except Exception as e:
                    raise TipException("翻译失败")
                if result.get("error_code") == "54003":
                    time.sleep(1)
                else:
                    break
        return "\n".join([item["dst"] for item in result["trans_result"]])


if __name__ == '__main__':
    trans = Translator()
    print(trans.translate("Test\nstring second \nstring"))
