import logging
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.config import PROJECT_ROOT
from app.routes.ping import router as ping_router
from app.routes.generate import ui_router, api_router

# 1) Налаштовуємо логування
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

# 2) Ініціалізуємо FastAPI
app = FastAPI()

# 3) Статичні файли
app.mount("/static", StaticFiles(directory=PROJECT_ROOT / "frontend/static"), name="static")

# 4) Підключаємо роутери
app.include_router(ping_router)    # /ping
app.include_router(ui_router)      # / & /generate (HTML)
app.include_router(api_router)     # /api/generate (JSON)
