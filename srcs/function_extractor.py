from .local_model import LocalLLM
from .prompt_builder import PromptBuilder
from .constrain_generation import GenerationController
class FunctionExtractor:
    def __init__(
        self,
        model:LocalLLM,
        prompt_builder: PromptBuilder,
        generation_controller: GenerationController
    ):
        if model is None:
            raise ValueError("model must not be None")
        if prompt_builder is None:
            raise ValueError("prompt_builder must not be None")
        if generation_controller is None:
            raise ValueError("generation_controller must not be None")
        self._model = model
        self._prompt_builder = prompt_builder
        self._generation_controller=generation_controller

    def extract_function_name(self, user_prompt: str):
        prompt = self._prompt_builder.setup_prompt(user_prompt)
        ids = self._model.encode(prompt)
        self._generation_controller.set_promt_length(ids.shape[1])
        return self._model.generate_function_name(
            ids,
            allowed_tokens_fn=self._generation_controller.constarain_tokens
            )