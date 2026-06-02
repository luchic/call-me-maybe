import json
import re
from typing import Any

from .local_model import LocalLLM
from .prompt_builder import PromptBuilder

class ArgumentExtractor:
    def __init__(
        self,
        model:LocalLLM,
        prompt_builder: PromptBuilder
    ):
        self._model = model
        self._prompt_builder = prompt_builder

    def extract_arguments(self, user_prompt: str, function_name: str):
        args = self._prompt_builder.get_function_arguments(function_name)
        if args is None:
            return {"arguments": {}}

        rule_based = self._extract_with_rules(user_prompt, function_name)
        if rule_based is not None and self._has_all_arguments(rule_based, args):
            return {"arguments": rule_based}

        extracted_args: dict[str, Any] = {}
        json_prefix = '{"arguments":{'

        for index, (argument_name, argument_schema) in enumerate(args.items()):
            if argument_name in rule_based:
                extracted_args[argument_name] = rule_based[argument_name]
                if index > 0:
                    json_prefix += ","
                json_prefix += (
                    f'"{argument_name}":'
                    f'{json.dumps(rule_based[argument_name])}'
                )
                continue

            if index > 0:
                json_prefix += ","
            json_prefix += f'"{argument_name}":'

            prompt = self._prompt_builder.setup_argument_slot_prompt_builder(
                user_prompt=user_prompt,
                function_name=function_name,
                argument_name=argument_name,
                argument_schema=argument_schema,
                json_prefix=json_prefix,
            )
            ids = self._model.encode(prompt)
            generated = self._model.generate(ids, max_new_tokens=20)
            value = self._normalize_generated_value(generated, argument_schema["type"])

            if value is not None:
                extracted_args[argument_name] = value
                json_prefix += json.dumps(value)
            else:
                json_prefix += "null"

        return {"arguments": extracted_args}

    def _extract_with_rules(
        self,
        user_prompt: str,
        function_name: str,
    ) -> dict[str, Any]:
        if function_name == "fn_add_numbers":
            numbers = self._extract_numbers(user_prompt)
            if len(numbers) >= 2:
                return {"a": numbers[0], "b": numbers[1]}

        if function_name == "fn_get_square_root":
            numbers = self._extract_numbers(user_prompt)
            if len(numbers) >= 1:
                return {"a": numbers[0]}

        if function_name == "fn_reverse_string":
            text = self._extract_primary_text(user_prompt)
            if text is not None:
                return {"s": text}

        if function_name == "fn_greet":
            name = self._extract_greet_name(user_prompt)
            if name is not None:
                return {"name": name}

        if function_name == "fn_substitute_string_with_regex":
            return self._extract_regex_substitution(user_prompt)

        return None

    def _has_all_arguments(
        self,
        extracted_args: dict[str, Any],
        function_args: dict[str, Any],
    ) -> bool:
        return all(argument_name in extracted_args for argument_name in function_args)

    def _extract_numbers(self, text: str) -> list[int | float]:
        normalized = text.replace(",", "")
        matches = re.findall(r"-?\d+(?:\.\d+)?", normalized)
        return [self._cast_number(match) for match in matches]

    def _cast_number(self, value: str) -> int | float:
        number = float(value)
        if number.is_integer():
            return int(number)
        return number

    def _extract_primary_text(self, text: str) -> str | None:
        quoted = self._extract_quoted_strings(text)
        if quoted:
            return quoted[0]

        match = re.search(
            r"(?:reverse|flip|mirror)\s+(?:the\s+)?(?:word|string|text|phrase)?\s*([A-Za-z0-9 _-]+)",
            text,
            re.IGNORECASE,
        )
        if match is None:
            return None
        return self._clean_span(match.group(1))

    def _extract_quoted_strings(self, text: str) -> list[str]:
        return [
            match.group(1) or match.group(2)
            for match in re.finditer(r'"([^"]+)"|\'([^\']+)\'', text)
        ]

    def _extract_greet_name(self, text: str) -> str | None:
        quoted = self._extract_quoted_strings(text)
        if quoted:
            return quoted[-1]

        patterns = (
            r"(?:greet|hello to|say hello to|welcome|salutation for)\s+(?:someone named\s+|my friend\s+)?([A-Z][\w.]+(?:\s+[A-Z][\w.]+)*)",
            r"(?:named|just greet)\s+([A-Z][\w.]+(?:\s+[A-Z][\w.]+)*)",
            r"\bgreet\s+([a-z][\w.]+)",
        )
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match is not None:
                return self._clean_span(match.group(1))
        return None

    def _extract_regex_substitution(self, text: str) -> dict[str, Any]:
        quoted = self._extract_quoted_strings(text)
        result: dict[str, Any] = {}

        if "source='" in text or 'source="' in text:
            source_match = re.search(r"source\s*=\s*['\"]([^'\"]+)['\"]", text)
            pattern_match = re.search(r"pattern\s*=\s*['\"]([^'\"]+)['\"]", text)
            replacement_match = re.search(
                r"replacement\s*=\s*['\"]([^'\"]+)['\"]", text
            )
            if source_match and pattern_match and replacement_match:
                return {
                    "source_string": source_match.group(1),
                    "regex": pattern_match.group(1),
                    "replacement": replacement_match.group(1),
                }

        if quoted:
            result["source_string"] = quoted[-1]

        regex = self._extract_regex_pattern(text, quoted)
        if regex is not None:
            result["regex"] = regex

        replacement = self._extract_replacement(text, quoted)
        if replacement is not None:
            result["replacement"] = replacement

        return result

    def _extract_regex_pattern(self, text: str, quoted: list[str]) -> str | None:
        lower = text.lower()
        if "number" in lower or "digit" in lower:
            return r"\d+"
        if "vowel" in lower:
            return r"[aeiouAEIOU]"
        if "space" in lower:
            return r"\s"
        if "commas" in lower or "comma" in lower:
            return ","
        if "dashes" in lower or "dash" in lower:
            return "-"

        if len(quoted) >= 3:
            return quoted[0]

        match = re.search(r"(?:substitute|replace|change)\s+(?:the word\s+)?['\"]?([^'\"]+?)['\"]?\s+(?:with|to|into)", text, re.IGNORECASE)
        if match is not None:
            return self._clean_span(match.group(1))

        return None

    def _extract_replacement(self, text: str, quoted: list[str]) -> str | None:
        if len(quoted) >= 3:
            return quoted[1]

        lower = text.lower()
        if "asterisk" in lower:
            return "*"
        if "underscore" in lower:
            return "_"
        if "semicolon" in lower:
            return ";"
        if "remove" in lower and ("dash" in lower or "dashes" in lower):
            return ""

        match = re.search(
            r"(?:with|to|into|using)\s+([A-Za-z0-9_@*;.-]+)",
            text,
            re.IGNORECASE,
        )
        if match is not None:
            return self._clean_span(match.group(1))

        return None

    def _clean_span(self, value: str) -> str:
        value = value.strip()
        value = re.sub(r"[.?!,;:]+$", "", value)
        return value.strip()

    def _normalize_generated_value(self, value: str, argument_type: str):
        value = self._clean_generated_value(value)
        if value == "" or value.lower() == "null":
            return None

        if argument_type == "number":
            return self._normalize_number(value)

        if argument_type == "string":
            return self._normalize_string(value)

        if argument_type == "boolean":
            return self._normalize_boolean(value)

        return value

    def _clean_generated_value(self, value: str) -> str:
        value = value.strip()
        value = value.splitlines()[0] if value else ""
        value = value.rstrip(",}")
        return value.strip()

    def _normalize_number(self, value: str):
        match = re.search(r"-?\d+(?:\.\d+)?", value)
        if match is None:
            return None

        return self._cast_number(match.group(0))

    def _normalize_string(self, value: str) -> str | None:
        if (
            (value.startswith('"') and value.endswith('"'))
            or (value.startswith("'") and value.endswith("'"))
        ):
            value = value[1:-1]

        value = value.strip()
        if value == "":
            return None
        return value

    def _normalize_boolean(self, value: str):
        value = value.lower()
        if value == "true":
            return True
        if value == "false":
            return False
        return None
