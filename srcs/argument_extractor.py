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
        print(user_prompt)
        print(function_name)
        system_prompt = self._prompt_builder.setup_extract_prompt_builder(user_prompt, function_name)
        args = self._prompt_builder.get_function_arguments(function_name)
        
        print(system_prompt)
        ids = self._model.encode(system_prompt)
        generated = self._model.generate(ids)
        print(generated)
