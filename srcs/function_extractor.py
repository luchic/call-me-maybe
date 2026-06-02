from .local_model import LocalLLM
from .prompt_builder import PromptBuilder

class FunctionExtractor:
    def __init__(
        self,
        model:LocalLLM,
        prompt_builder: PromptBuilder
    ):
        self._model = model
        self._prompt_builder = prompt_builder
