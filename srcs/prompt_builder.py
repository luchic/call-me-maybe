import json
from pathlib import Path
from typing import Any
from .mappers.system_prompt_validator import SystemPromptValidator


class PromptBuilder:
    def __init__(self, source: str | Path) -> None:
        if not isinstance(source, str | Path):
            raise TypeError("source must be a string path or pathlib.Path")

        self._source = Path(source)
        self._validator = SystemPromptValidator()
        self._data = self._read_data()
    
    def setup_prompt(self, user_prompt: str) -> str:
        prompt = f"""You are a function router.

Choose exactly one function name.
Rules:
 - Output only one function name.
 - Do not explain.
 - Do not add punctuation.
 - The output must be one of the allowed function names.
 - If no function match you have to return fn_none function
 - Do not use a function just because the prompt contains numbers or text.
 - All required parameters for the function must be clearly present in the user request.

Available functions:{self._get_function_defention_text()}
\t - fn_none: if you can't match user prompt to any function you have to call this function
User request: {user_prompt}

Function name:"""

        return prompt
    
    def setup_extract_prompt_builder(self, user_prompt:str, function_name:str):
        prompt = f"""You are an argument extraction engine.

Extract only the arguments required by the function from the user's message.

Rules:
- Output only extracted argument values.
- Do not explain.
- Do not add labels, punctuation, or extra text.
- Output a single line.
- Separate multiple arguments with a single space.
- Preserve the exact user wording for extracted values unless normalization is explicitly required.
- Output arguments in this exact order: <arg1> <arg2> <arg3>.
- If an argument is missing or unclear, omit it.
- If no arguments can be extracted, output an empty line.

Function: {function_name}

Function description: {self._get_function_description(function_name)}

Arguments: {self._get_function_argumetns(function_name)}

User message: {user_prompt}

Now extract only arguments from user prompt: """
        return prompt

    def _get_function_description(self, function_name:str):
        for function in self._data:
            if function['name'] == function_name:
                return function['description']
        return "Function not found" # I should change this mechanism

    def _get_function_argumetns(self, function_name:str):
        function = None
        for tmp in self._data:
            if tmp['name'] == function_name:
                function = tmp
                break
        if (function is None):
            return "None"
        result = ""
        for key, value in function["parameters"].items():
            result += f"\n- {key}: type is {value['type']} "
        return result

    def _read_data(self) -> list[dict[str, Any]]:
        data = json.loads(self._read_text())
        self._validator.validate(data)
        return data

    def _read_text(self) -> str:
        return self._source.read_text(encoding="utf-8")

    def _get_function_defention_text(self) -> str:
        result = ""
        for index, function in enumerate(self._data):
            result += f"\n\t - {function['name']}: {function['description']}" 
        return result
    
    def get_function_arguments(self, function_name):
        function = None
        for tmp in self._data:
            if tmp['name'] == function_name:
                function = tmp
                break
        if (function is None):
            return None
        return function["parameters"]
