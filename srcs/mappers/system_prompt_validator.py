from typing import Any

class SystemPromptValidator:
    """
    Example of validatated data.
    [
        {
            "name": "fn_add_numbers",
            "description": "Add two numbers together and return their sum.",
            "parameters": {
            "a": {
                "type": "number"
            },
            "b": {
                "type": "number"
            }
            },
            "returns": {
            "type": "number"
            }
        },
        {
            "name": "fn_greet",
            "description": "Generate a greeting message for a person by name.",
            "parameters": {
            "name": {
                "type": "string"
            }
            },
            "returns": {
            "type": "string"
            }
        }
    ]
    """
    ALLOWED_TYPES = ("string", "number", "boolean", "array", "object", "null")
    def validate(self, data: Any) -> None:
        if not isinstance(data, list):
            raise ValueError("Input must be a JSON array")

        seen_names: set[str] = set()
        for index, item in enumerate(data):
            if not isinstance(item, dict):
                raise ValueError(f"Input item {index} must be an object")

            name = self._validate_function_definition(item, index)
            if name in seen_names:
                raise ValueError(f"Input item {index} has duplicate function name '{name}'")
            seen_names.add(name)

    def _validate_function_definition(self, data: dict[str, Any], index: int) -> str:
        name = data.get("name")
        if not isinstance(name, str) or name == "":
            raise ValueError(f"Input item {index} must contain a non-empty string 'name'")

        description = data.get("description")
        if not isinstance(description, str) or description == "":
            raise ValueError(
                f"Input item {index} must contain a non-empty string 'description'"
            )

        parameters = data.get("parameters")
        if not isinstance(parameters, dict):
            raise ValueError(f"Input item {index} must contain an object 'parameters'")

        for parameter_name, parameter_schema in parameters.items():
            self._validate_parameter(index, parameter_name, parameter_schema)

        returns = data.get("returns")
        self._validate_type_schema(index, "returns", returns)
        return name

    def _validate_parameter(
        self, function_index: int, parameter_name: Any, parameter_schema: Any
    ) -> None:
        if not isinstance(parameter_name, str) or parameter_name == "":
            raise ValueError(
                f"Input item {function_index} has a parameter with an invalid name"
            )

        self._validate_type_schema(
            function_index,
            f"parameters.{parameter_name}",
            parameter_schema,
        )

    def _validate_type_schema(
        self, function_index: int, field_name: str, schema: Any
    ) -> None:
        if not isinstance(schema, dict):
            raise ValueError(f"Input item {function_index} '{field_name}' must be an object")

        type_name = schema.get("type")
        if not isinstance(type_name, str) or type_name == "":
            raise ValueError(
                f"Input item {function_index} '{field_name}' must contain a "
                "non-empty string 'type'"
            )

        if type_name not in self.ALLOWED_TYPES:
            allowed = ", ".join(sorted(self.ALLOWED_TYPES))
            raise ValueError(
                f"Input item {function_index} '{field_name}' has unsupported type "
                f"'{type_name}'. Allowed types: {allowed}"
            )
