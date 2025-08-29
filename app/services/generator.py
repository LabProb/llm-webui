# app/services/generator.py

from pathlib import Path
from app.llm.llama_wrapper import LlamaModel

PROJECT_ROOT = Path(__file__).resolve().parents[2]
MODELS_DIR = PROJECT_ROOT / "models"

DEFAULT_STOP = ["User:", "Assistant:", "</s>"]
DEFAULT_PARAMS = {
    "max_tokens": 256,
    "temperature": 0.8,
    "top_p": 0.9,
    "repeat_penalty": 1.2,
    "stop": DEFAULT_STOP
}

def list_models() -> list[str]:
    if not MODELS_DIR.exists():
        return []
    return [f.name for f in sorted(MODELS_DIR.glob("*.gguf"))]

def build_prompt(user_input: str) -> str:
    return (
        "You are a concise assistant.\n"
        f"User: {user_input}\n"
        "Assistant:"
    )

def generate_response(
    user_input: str,
    model_name: str | None = None,
    max_tokens: int = DEFAULT_PARAMS["max_tokens"],
    temperature: float = DEFAULT_PARAMS["temperature"],
    top_p: float = DEFAULT_PARAMS["top_p"],
    repeat_penalty: float = DEFAULT_PARAMS["repeat_penalty"],
) -> tuple[str, int]:
    prompt = build_prompt(user_input)
    model_path = MODELS_DIR / model_name if model_name else None
    llama = LlamaModel(model_path=str(model_path) if model_path else None)

    return llama.generate(
        prompt=prompt,
        max_tokens=max_tokens,
        stop=DEFAULT_PARAMS["stop"],
        temperature=temperature,
        top_p=top_p,
        repeat_penalty=repeat_penalty
    )
