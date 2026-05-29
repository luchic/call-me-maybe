import torch

class GenerationController:
    prompt_length = 0
    allowed_tokens = None
    prefix_token = None
    eof_token = None

    def set_promt_length(self, length: int):
        self.prompt_length = length
    
    def set_allowed_toknes(self, tokens: list[torch.Tensor]):
        data = []
        for token in tokens:
            token = token.flatten().tolist()
            data.append(token)    
        self.allowed_tokens = data

    def set_prefix_function_name_token(self, prefix: torch.Tensor):
        self.prefix_token = prefix.flatten().tolist()


    def set_eof_token(self, eof_token):
        self.eof_token = eof_token

    def get_set_of_tokens(self):
        result = set()
        for token in self.allowed_tokens:
            result.update(token)
        return list(result)

    def constarain_tokens(self, batch_id, input_ids):
        generated = input_ids[self.prompt_length:].tolist()
        if (len(generated) < len(self.prefix_token)):
            return self.prefix_token
        
        next_tokens = []
        for allowed in self.allowed_tokens:
            if allowed[:len(generated)] != generated:
                continue
            if len(generated) == len(allowed):
                return [self.eof_token]
            next_tokens.append(allowed[len(generated)])

        if (len(next_tokens) == 0):
            return [self.eof_token]
        return next_tokens
