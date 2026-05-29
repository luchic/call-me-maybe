import torch
import torch.nn.functional as F
from transformers import AutoModelForCausalLM, AutoTokenizer, PreTrainedTokenizer, PreTrainedModel, logging
from huggingface_hub import hf_hub_download
from typing import Callable
from typing import Optional



logging.set_verbosity_error()  # keep the console clean


class LocalLLM:
    """Utility class wrapping a lightweight Hugging Face causal-LM for fast, low-memory experimentation.

    Parameters
    ----------
    model_name: str, default="Qwen/Qwen3-0.6B"
        Identifier of the model on the HF Hub.
    device: str | None, default=None
        Computation device. If *None* we automatically select ``mps`` when available on macOS,
        ``cuda`` when available, otherwise we fall back to ``cpu``.
    dtype: torch.dtype | None, default=None
        Numerical precision. When using a GPU or MPS we default to ``float16`` to keep memory
        usage reasonable; on CPU we keep ``float32`` for maximum compatibility.
    """

    def __init__(
        self,
        model_name: str = "Qwen/Qwen3-0.6B",
        *,
        device: str | None = None,
        dtype: torch.dtype | None = None,
        trust_remote_code: bool = True,
    ) -> None:
        self._model_name = model_name

        # Auto-select device with priority: mps > cuda > cpu
        if device is None:
            if torch.backends.mps.is_available():
                device = "mps"
            elif torch.cuda.is_available():
                device = "cuda"
            else:
                device = "cpu"
        self._device = device

        if dtype is None:
            dtype = torch.float16 if self._device in ["cuda", "mps"] else torch.float32
        self._dtype = dtype

        # --- load tokenizer & model -------------------------------------------------
        self._tokenizer: PreTrainedTokenizer = AutoTokenizer.from_pretrained(
            model_name, trust_remote_code=trust_remote_code
        )
        if self._tokenizer.pad_token_id is None:
            # ensure we have a pad token to keep batch helpers happy
            self._tokenizer.pad_token_id = self._tokenizer.eos_token_id

        self._model: PreTrainedModel = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=self._dtype,
            device_map="auto" if self._device == "cuda" else None,
            trust_remote_code=trust_remote_code,
        )
        self._model.to(self._device)
        self._model.eval()

        # switch to inference-only mode
        for p in self._model.parameters():
            p.requires_grad = False


    def encode(self, text: str) -> torch.Tensor:
        """Tokenise *text* and return a 2-D ``input_ids`` tensor on the target device."""
        return self._tokenizer.encode(text, add_special_tokens=False, return_tensors="pt")
    
    def encode_list(self, texts: list[str]) -> list[torch.Tensor]:
        encoded_textes = [
            self.encode(text)
            for text in texts ]
        return encoded_textes

    def decode(self, ids: torch.Tensor | list[int]) -> str:
        """Inverse of :py:meth:`encode`. Removes special tokens."""
        if isinstance(ids, torch.Tensor):
            ids = ids.squeeze(0).tolist()
        return self._tokenizer.decode(ids, skip_special_tokens=True)

    def ids_to_list(self, ids: torch.Tensor | list[int]) -> list[int]:
        if isinstance(ids, torch.Tensor):
            ids = ids.flatten().tolist()
        return [int(token_id) for token_id in ids]
    
    def get_eof_token_id(self):
        return self._tokenizer.eos_token_id

    def generate_with_probabilities(
        self, ids: torch.Tensor,
        allowed_tokens_fn: Optional[Callable[[int, torch.Tensor], list[int]]] = None
    ) -> torch.Tensor:
        """Generate text from *ids*.

        By default this returns only the newly generated tokens. Set
        ``include_prompt=True`` to decode the prompt together with the completion.

        """
        with torch.no_grad():
            output_ids = self._model.generate(input_ids=ids,
                max_new_tokens=10,
                do_sample=False,
                num_beams=1,
                prefix_allowed_tokens_fn=allowed_tokens_fn,
                pad_token_id=self._tokenizer.pad_token_id,
                eos_token_id=self._tokenizer.eos_token_id,
                return_dict_in_generate=True,
                output_scores=True,              
            )

        transition_scores = self._model.compute_transition_scores(
            output_ids.sequences,
            output_ids.scores,
            normalize_logits=True,
        )

        token_log_probs = transition_scores[0]
        token_probs = torch.exp(token_log_probs)
        answer_probability = token_probs.prod().item()
        genereted = output_ids.sequences[:, ids.shape[-1]:]
        return genereted, answer_probability

    def generate_function_name(
        self, ids: torch.Tensor,
        none_function="ft_none",
        allowed_tokens_fn: Optional[Callable[[int, torch.Tensor], list[int]]] = None
    ) -> torch.Tensor:
        """Generate text from *ids*.

        By default this returns only the newly generated tokens. Set
        ``include_prompt=True`` to decode the prompt together with the completion.

        """
        with torch.no_grad():
            output_ids = self._model.generate(input_ids=ids,
                max_new_tokens=10,
                do_sample=False,
                num_beams=1,
                prefix_allowed_tokens_fn=allowed_tokens_fn,
                pad_token_id=self._tokenizer.pad_token_id,
                eos_token_id=self._tokenizer.eos_token_id,
                return_dict_in_generate=True,
                output_scores=True,              
            )

        transition_scores = self._model.compute_transition_scores(
            output_ids.sequences,
            output_ids.scores,
            normalize_logits=True,
        )
        token_log_probs = transition_scores[0]
        token_probs = torch.exp(token_log_probs)
        answer_probability = token_probs.prod().item()

        if (answer_probability < 0.98):
            return none_function 
        genereted = output_ids.sequences[:, ids.shape[-1]:]
        return self.decode(genereted)

    def generate(
        self, ids: torch.Tensor,
        allowed_tokens_fn: Optional[Callable[[int, torch.Tensor], list[int]]] = None
    ) -> str:
        """Generate text from *ids*.

        By default this returns only the newly generated tokens. Set
        ``include_prompt=True`` to decode the prompt together with the completion.

        """
        with torch.no_grad():
            output_ids = self._model.generate(input_ids=ids,
                max_new_tokens=10,
                do_sample=False,
                num_beams=1,
                prefix_allowed_tokens_fn=allowed_tokens_fn,
                pad_token_id=self._tokenizer.pad_token_id,
                eos_token_id=self._tokenizer.eos_token_id       
            )

        return self.decode(output_ids[:, ids.shape[-1]:])
