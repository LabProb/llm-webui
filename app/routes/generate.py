import logging
import asyncio
import time

from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field

from app.config import PROJECT_ROOT
from app.services.generator import (
    list_models,
    generate_response,
    DEFAULT_PARAMS,
)

ui_router = APIRouter()
api_router = APIRouter(prefix="/api", tags=["api"])
templates = Jinja2Templates(directory=PROJECT_ROOT / "frontend/templates")


# === UI-маршрути (без змін) ===
@ui_router.get("/", response_class=HTMLResponse)
async def form_get(request: Request):
    models = list_models()
    context = {
        "request": request,
        "models": models,
        "selected_model": None,
        **DEFAULT_PARAMS,
        "defaults": DEFAULT_PARAMS,
    }
    return templates.TemplateResponse("index.html", context)


@ui_router.post("/generate", response_class=HTMLResponse)
async def form_post(
    request: Request,
    model: str | None = Form(None, max_length=255),
    prompt: str = Form(..., min_length=1, max_length=10_000),
    max_tokens: int = Form(DEFAULT_PARAMS["max_tokens"], ge=1, le=2048),
    temperature: float = Form(DEFAULT_PARAMS["temperature"], ge=0, le=2),
    top_p: float = Form(DEFAULT_PARAMS["top_p"], ge=0, le=1),
    repeat_penalty: float = Form(DEFAULT_PARAMS["repeat_penalty"], ge=1, le=2),
):
    start = time.time()
    models = list_models()

    response_text, token_count = await asyncio.to_thread(
        generate_response,
        user_input=prompt,
        model_name=model,
        max_tokens=max_tokens,
        temperature=temperature,
        top_p=top_p,
        repeat_penalty=repeat_penalty,
    )
    duration = round(time.time() - start, 3)
    logging.info(
        f"UI /generate | model={model} | max_tokens={max_tokens} "
        f"| temp={temperature} | p={top_p} | rp={repeat_penalty} "
        f"| {duration}s | tokens={token_count}"
    )

    context = {
        "request": request,
        "models": models,
        "selected_model": model,
        "prompt": prompt,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "top_p": top_p,
        "repeat_penalty": repeat_penalty,
        "defaults": DEFAULT_PARAMS,
        "response": response_text,
        "tokens": token_count,
        "duration": duration,
    }
    return templates.TemplateResponse("index.html", context)


# === API-модель запиту/відповіді ===

class GenerateRequest(BaseModel):
    prompt: str = Field(min_length=1, max_length=10_000)
    model: str | None = Field(default=None, max_length=255)
    max_tokens: int = Field(default=DEFAULT_PARAMS["max_tokens"], ge=1, le=2048)
    temperature: float = Field(default=DEFAULT_PARAMS["temperature"], ge=0, le=2)
    top_p: float = Field(default=DEFAULT_PARAMS["top_p"], ge=0, le=1)
    repeat_penalty: float = Field(default=DEFAULT_PARAMS["repeat_penalty"], ge=1, le=2)


class GenerateResponse(BaseModel):
    response: str
    tokens: int
    duration: float


@api_router.post(
    "/generate",
    response_model=GenerateResponse,
    responses={422: {"description": "Validation Error"}},
)
async def api_generate(req: GenerateRequest):
    start = time.time()
    try:
        response_text, token_count = await asyncio.to_thread(
            generate_response,
            user_input=req.prompt,
            model_name=req.model,
            max_tokens=req.max_tokens,
            temperature=req.temperature,
            top_p=req.top_p,
            repeat_penalty=req.repeat_penalty,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        logging.exception("API /generate failed")
        raise HTTPException(status_code=500, detail="Generation failed") from e

    duration = round(time.time() - start, 3)
    return GenerateResponse(
        response=response_text,
        tokens=token_count,
        duration=duration,
    )
