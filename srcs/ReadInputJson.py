import json
from pathlib import Path
from typing import Any


class ReadInputJson:
    def __init__(self, source: str | Path) -> None:
        if not isinstance(source, str | Path):
            raise TypeError("source must be a string path or pathlib.Path")

        self.source = Path(source)
        if not self.source.exists():
            raise FileNotFoundError(f"File not found: {self.source}")

        if not self.source.is_file():
            raise ValueError(f"Path is not a file: {self.source}")
    
    def read(self) -> list[str]:
        data = self.read_raw()
        return self._extract_prompts(data)

    def read_raw(self) -> list[dict[str, Any]]:
        data = json.loads(self._read_text())
        self._validate(data)
        return data

    def _read_text(self) -> str:
        return self.source.read_text(encoding="utf-8")

    def _validate(self, data: Any) -> None:
        if not isinstance(data, list):
            raise ValueError("Input must be a JSON array")

        for index, item in enumerate(data):
            if not isinstance(item, dict):
                raise ValueError(f"Input item {index} must be an object")

            prompt = item.get("prompt")
            if not isinstance(prompt, str) or prompt == "":
                raise ValueError(f"Input item {index} must contain a string 'prompt'")

    def _extract_prompts(self, data: list[dict[str, Any]]) -> list[str]:
        return [item["prompt"] for item in data]
