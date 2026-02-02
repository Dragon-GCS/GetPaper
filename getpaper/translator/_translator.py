from abc import ABC, abstractmethod


class _Translator(ABC):
    @abstractmethod
    async def translate(self, detail: str) -> str: ...
