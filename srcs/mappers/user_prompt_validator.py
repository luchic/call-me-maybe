from typing import Any

class UserpromptValidator:
    
    def validate(self, data: Any) -> None:
        if not isinstance(data, list):
            raise ValueError("Input must be a JSON array")

        for index, item in enumerate(data):
            if not isinstance(item, dict):
                raise ValueError(f"Input item {index} must be an object")

            prompt = item.get("prompt")
            if not isinstance(prompt, str) or prompt == "":
                raise ValueError(f"Input item {index} must contain a string 'prompt'")

