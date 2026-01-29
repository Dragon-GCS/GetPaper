from abc import ABC, abstractmethod


class _Translator(ABC):
    @abstractmethod
    def translate(self, detail: str) -> str: ...
