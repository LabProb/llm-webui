# app/config.py
from pathlib import Path

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MODEL_DIR = PROJECT_ROOT / "models"


class Settings(BaseSettings):
    # Якщо ENV-перемінних з префіксом не потрібно — залишаємо порожній рядок
    model_config = SettingsConfigDict(
        env_prefix="",      # без префікса ENV
        env_file=".env",    # автопідхват змінних із .env (опціонально)
    )

    model_dir: Path = Field(default=DEFAULT_MODEL_DIR)
    model_name: str | None = None
    n_ctx: int = 2048
    frontend_path: Path = PROJECT_ROOT / "frontend/index.html"

    @model_validator(mode="before")
    @classmethod
    def pick_first_model(cls, values: dict) -> dict:
        if values.get("model_name"):
            return values

        dir_path = Path(values.get("model_dir", DEFAULT_MODEL_DIR))
        candidates = sorted(dir_path.glob("*.gguf"))
        if not candidates:
            raise RuntimeError(f"No .gguf files found in {dir_path!r}")
        values["model_name"] = candidates[0].name
        return values

    @property
    def model_path(self) -> str:
        return str(self.model_dir / self.model_name)


settings = Settings()
