from .reader import ReadInputJson
from .prompt_builder import PromptBuilder
from .local_model import LocalLLM

def main():
    reader = ReadInputJson("./data/input/function_calling_tests.json")
    builder = PromptBuilder("./data/input/functions_definition.json")
    model = LocalLLM(device="cpu")
    
    text = reader.read()
    for index, text in enumerate(text):
        prompt = builder.setup_prompt(text)
        ids = model.encode(prompt)
        generated = model.generate(ids)
        print(index, "==== generated ======")
        print(generated)


if __name__ == "__main__":
    main()
