from .reader import ReadInputJson
from .prompt_builder import PromptBuilder
from .local_model import LocalLLM
from .functions import FunctionRunner
from .constrain_generation import GenerationController
from .argument_extractor import ArgumentExtractor

def main():
    # reader = ReadInputJson("./data/input/wrong-input.json")
    # reader = ReadInputJson("./data/input/test-input.json")
    # reader = ReadInputJson("./data/input/small-input.json")
    # reader = ReadInputJson("./data/input/small-wrong.json")
    reader = ReadInputJson("./data/input/function_calling_tests.json")
    builder = PromptBuilder("./data/input/functions_definition.json")
    model = LocalLLM(device="cpu")
    runner = FunctionRunner()
    controller = GenerationController()
    extractor = ArgumentExtractor(model=model, prompt_builder=builder)

    allowed = runner.get_simple_function_naming()
    prefix = runner.get_prefix_of_function()
    allowed_ids = model.encode_list(allowed)
    prefix_ids = model.encode(prefix)    
    controller.set_allowed_toknes(allowed_ids)
    controller.set_prefix_function_name_token(prefix_ids)
    controller.set_eof_token(model.get_eof_token_id())

    text = reader.read()
    for index, text in enumerate(text):
        prompt = builder.setup_prompt(text)
        ids = model.encode(prompt)
        controller.set_promt_length(ids.shape[1])
        generated = model.generate_function_name(ids, allowed_tokens_fn=controller.constarain_tokens)
        print(index, "==== generated ======")
        print(generated)
        if (generated != "fn_none"):
            result = extractor.extract_arguments(text, generated)
            print(result)



if __name__ == "__main__":
    main()
