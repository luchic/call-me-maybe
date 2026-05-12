import torch


def create_random_ids(length: int, device: str | torch.device | None = None) -> torch.Tensor:
    """Return one row of random ids in the inclusive range 1..10000."""
    if length <= 0:
        raise ValueError("length must be greater than 0")

    return torch.randint(1, 40001, (1, length), device=device, dtype=torch.long)


if __name__ == "__main__":
    from llm_sdk import Small_LLM_Model

    model = Small_LLM_Model()

    # # prompt = "Write one short sentence about Python programming:"
    prompt= """
You are a function selector.

Choose one function from this list:

add(a, b) - use when user wants addition
subtract(a, b) - use when user wants subtraction
multiply(a, b) - use when user wants multiplication
divide(a, b) - use when user wants division

Return ONLY valid JSON.

Examples:

User: calculate 5 + 6
{"function": "add", "a": 5, "b": 6}

User: what is 10 minus 3
{"function": "subtract", "a": 10, "b": 3}

User: multiply 4 by 7
{"function": "multiply", "a": 4, "b": 7}

Now you will get a user prompt.

Halloe what is your name?
"""
# From user interface i need to 
    ids = model.encode(prompt)
    # ids = create_random_ids(20)
    txt = model.generate(ids, max_new_tokens=40)
    print(txt)

    # new_ids = model.encode(txt)
    # new_txt = model.generate(new_ids, max_new_tokens=40)
    # print(new_txt)

# I need to understand the error messages. The error message is
# "No such file or directory" when trying to open a file.
# The problem is that the file is not found, so
#  is in English: "I want to see you.
# Please don't let me know if I'm in danger.
# I'm not safe here. I'm not safe here."