import math
import re


class FunctionRunner:
    GREET = "greet"
    SUM = "add"
    REVERSE = "reverse_string"
    SQUARE_ROOT = "square_root"
    REGEX = "substitute_string_with_regex"
    
    """
        It's first version. Because i'm not sure how should i handle it.
        Some funcion return valuse. Some functions schould print something.
        So I thinks i need to change it later.
    """
    def fn_add_numbers(self, a: float, b: float) -> float:
        return a + b

    def fn_greet(self, name: str) -> str:
        return f"Hello, {name}!"

    def fn_reverse_string(self, s: str) -> str:
        return s[::-1]

    def fn_get_square_root(self, a: float) -> float:
        return math.sqrt(a)

    def fn_substitute_string_with_regex(
        self, source_string: str, regex: str, replacement: str
    ) -> str:
        return re.sub(regex, replacement, source_string)

    def run(self, function_name: str, *args):
        if function_name == "fn_add_numbers":
            return self.fn_add_numbers(*args)

        if function_name == "fn_greet":
            return self.fn_greet(*args)

        if function_name == "fn_reverse_string":
            return self.fn_reverse_string(*args)

        if function_name == "fn_get_square_root":
            return self.fn_get_square_root(*args)

        if function_name == "fn_substitute_string_with_regex":
            return self.fn_substitute_string_with_regex(*args)

        raise ValueError(f"Unknown function: {function_name}")
    
    def get_simple_function_naming(self) -> list:
        return [
            self.GREET,
            self.SUM,
            self.REVERSE,
            self.SQUARE_ROOT,
            self.REGEX
        ]
