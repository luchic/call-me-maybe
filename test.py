import re
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM


model_name = "Qwen/Qwen2.5-0.5B-Instruct"

tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
    device_map="auto"
)

functions = {
    "fn_add_numbers": lambda a, b: a + b,
    "fn_greet": lambda a, b: a - b,
    "fn_reverse_string": lambda a, b: a * b,
    "fn_get_square_root": lambda a, b: a / b,
    "fn_substitute_string_with_regex": lambda a, b: a / b,
}

choices = list(functions.keys())
choice_token_ids = [
    tokenizer.encode(choice, add_special_tokens=False)
    for choice in choices
]

eos_id = tokenizer.eos_token_id


def choose_function(user_text: str) -> str:
    prompt = f"""You are a function router.

Choose exactly one function name.

Available functions:
	- fn_add_numbers: Add two numbers together and return their sum. 
    - fn_greet: Generate a greeting message for a person by name.
    - fn_reverse_string: Reverse a string and return the reversed result.
    - fn_get_square_root: Calculate the square root of a number.
    - fn_substitute_string_with_regex: Replace all occurrences matching a regex pattern in a string.

User request: {user_text}

Function name:"""

    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    prompt_len = inputs["input_ids"].shape[1]

    def allowed_tokens_fn(batch_id, input_ids):
        generated = input_ids[prompt_len:].tolist()
        allowed = []

        for choice_ids in choice_token_ids:
            if generated == choice_ids[:len(generated)]:
                if len(generated) < len(choice_ids):
                    allowed.append(choice_ids[len(generated)])
                else:
                    allowed.append(eos_id)

        return list(set(allowed)) if allowed else [eos_id]

    output_ids = model.generate(
        **inputs,
        max_new_tokens=10,
        do_sample=False,
        num_beams=1,
        prefix_allowed_tokens_fn=allowed_tokens_fn,
        eos_token_id=eos_id,
        pad_token_id=eos_id,
    )

    generated_ids = output_ids[0][prompt_len:]
    return tokenizer.decode(generated_ids, skip_special_tokens=True).strip()


def extract_two_numbers(text: str):
    nums = re.findall(r"-?\d+(?:\.\d+)?", text)
    if len(nums) < 2:
        raise ValueError("Could not find two numbers")

    a = float(nums[0])
    b = float(nums[1])

    return a, b

# user_promts = [
#   {
#     "prompt": "What is the sum of 2 and 3?"
#   },
#   {
#     "prompt": "What is the sum of 265 and 345?"
#   },
#   {
#     "prompt": "Greet shrek"
#   },
#   {
#     "prompt": "Greet john"
#   },
#   {
#     "prompt": "Reverse the string 'hello'"
#   },
#   {
#     "prompt": "Reverse the string 'world'"
#   	"What is the square root of 16?"
#     "Calculate the square root of 144"
# 	"Replace all numbers in \"Hello 34 I'm 233 years old\" with NUMBERS"
#     "Replace all vowels in 'Programming is fun' with asterisks"
#    	"Substitute the word 'cat' with 'dog' in 'The cat sat on the mat with another cat'"
# ]



user_text = "Make some sume john and mark"

print("Getting the name")
function_name = choose_function(user_text)
# a, b = extract_two_numbers(user_text)

# answer = functions[function_name](a, b)

print("Function:", function_name)
# print("Arguments:", a, b)
# print("Answer:", answer)