from .reader import InputReader
from .argument_extractor import ArgumentExtractor
from .function_extractor import FunctionExtractor

class Pipeline:
    _reader = None | InputReader

    def __init__(
            self,
            reader : InputReader,
            function_extractor: FunctionExtractor,
            argument_extractor: ArgumentExtractor
        ):
        if reader is None:
            raise ValueError("reader must not be None")
        if function_extractor is None:
            raise ValueError("function_extractor must not be None")
        if argument_extractor is None:
            raise ValueError("argument_extractor must not be None")
        self._reader = reader
        self._function_extractor = function_extractor
        self._argument_extractor = argument_extractor

    def run(self):
        dict = {
            "function":None,
            "arguments":None,
        }

        for prompt in self._reader.read_next():
            function_name = self._function_extractor.extract_function_name(prompt)
            args = self._argument_extractor.extract_arguments(prompt, function_name)
            dict["function"] = function_name
            dict["arguments"] = args["arguments"]
            print(dict)