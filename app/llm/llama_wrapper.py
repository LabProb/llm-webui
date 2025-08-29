# app/llm/llama_wrapper.py
import logging
from llama_cpp import Llama
from app.config import settings


class LlamaModel:
    """
    A wrapper around llama_cpp.Llama that takes a path to a .gguf file.
    If model_path is not provided, settings.model_path is used.
    """
    def __init__(self, model_path: str | None = None):
        path = model_path or settings.model_path
        logging.info(f"Loading the model: {path}")
        self.llm = Llama(
            model_path=path,
            n_ctx=settings.n_ctx,
            verbose=False
        )

    def generate(
        self,
        prompt: str,
        max_tokens: int = 256,
        stop: list[str] | None = None,
        temperature: float = 0.8,
        top_p: float = 0.9,
        repeat_penalty: float = 1.2
    ) -> tuple[str, int]:
        args = {
            "prompt": prompt,
            "max_tokens": max_tokens,
            "stop": stop or [],
            "temperature": temperature,
            "top_p": top_p,
            "repeat_penalty": repeat_penalty,
            "echo": False
        }
        output = self.llm(**args)
        text = output["choices"][0]["text"].strip().lstrip(":* \n")
        tokens = output.get("usage", {}).get("total_tokens", 0)
        logging.info(f"Prompt: {prompt[:50]}… → Tokens: {tokens}")
        return text, tokens
