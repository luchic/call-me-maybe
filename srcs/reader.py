import json
from pathlib import Path
from typing import Any, Iterator
from .mappers.user_prompt_validator import UserPromptValidator

from abc import ABC, abstractmethod
class InputReader(ABC):
    @abstractmethod
    def read_next(self) -> Iterator[str]:
        pass

class ReadInputJson(InputReader):
    def __init__(self, source: str | Path) -> None:
        if not isinstance(source, str | Path):
            raise TypeError("source must be a string path or pathlib.Path")

        self.source = Path(source)
        self.validator = UserPromptValidator()
        if not self.source.exists():
            raise FileNotFoundError(f"File not found: {self.source}")

        if not self.source.is_file():
            raise ValueError(f"Path is not a file: {self.source}")
    
    def read_next(self):
        data = self._read()
        for prompt in data:
            yield prompt

    def _read(self) -> list[str]:
        data = self.read_raw()
        return self._extract_prompts(data)

    def read_raw(self) -> list[dict[str, Any]]:
        data = json.loads(self._read_text())
        self.validator.validate(data)
        return data

    def _read_text(self) -> str:
        return self.source.read_text(encoding="utf-8")

    def _extract_prompts(self, data: list[dict[str, Any]]) -> list[str]:
        return [item["prompt"] for item in data]
