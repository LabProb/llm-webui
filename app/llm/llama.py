# app/llm/llama.py
from app.config import settings
from llama_cpp import Llama

llm = None

def load_model():
    global llm
    if llm is None:
        print(f"Loading model from {settings.model_path}...")
        llm = Llama(model_path=settings.model_path)
        print("Model loaded.")

def generate(prompt: str) -> str:
    load_model()
    result = llm(prompt)
    return result["choices"][0]["text"]
