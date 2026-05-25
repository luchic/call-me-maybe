import json
from pathlib import Path
from typing import Any
from mappers.system_prompt_validator import SystemPromptValidator


class PromptBuilder:
    def __init__(self, source: str | Path) -> None:
        if not isinstance(source, str | Path):
            raise TypeError("source must be a string path or pathlib.Path")

        self.source = Path(source)
        self.validator = SystemPromptValidator()
        self.data = self._read_data()

    def _read_data(self) -> list[dict[str, Any]]:
        data = json.loads(self._read_text())
        self.validator.validate(data)
        return data

    def _read_text(self) -> str:
        return self.source.read_text(encoding="utf-8")

    def setup_prompt(self, user_prompt: str) -> str:
        prompt = f"""You are a function router.

Choose exactly one function name.

Available functions:{self._get_function_defention_text()}
User request: {user_prompt}

Function name:"""

        return prompt
    
    def _get_function_defention_text(self) -> str:
        result = ""
        for index, function in enumerate(self.data):
            result += f"\n\t - {function['name']}: {function['description']}"
        return result
