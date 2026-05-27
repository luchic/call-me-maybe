import torch

class GenerationController:
    prompt_length = 0
    allowed_tokens = None
    eof_token = None

    def set_promt_length(self, length: int):
        self.prompt_length = length
    
    def set_allowed_toknes(self, tokens: list[torch.Tensor]):
        data = []
        for token in tokens:
            token = token.flatten().tolist()
            data.append(token)    
        self.allowed_tokens = data

    def set_eof_token(self, eof_token):
        self.eof_token = eof_token

    def get_set_of_tokens(self):
        result = set()
        for token in self.allowed_tokens:
            result.update(token)
        return list(result)

    def constarain_tokens(self, batch_id, input_ids):
        generated = input_ids[self.prompt_length:].tolist()
        if (len(generated) == 0):
            return self.get_set_of_tokens()

        to_print = set()
        for allowed in self.allowed_tokens:
            if generated == allowed:
                return list((self.eof_token,))
            if generated[-1] in allowed:
                to_print.update(allowed)
        return list(to_print)