# app/routes/generate.py

import time
import logging

from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi import Form
from pydantic import BaseModel

from app.services.generator import (
    list_models,
    generate_response,
    DEFAULT_PARAMS,
)

ui_router = APIRouter()
api_router = APIRouter(prefix="/api", tags=["api"])
templates = Jinja2Templates(directory="frontend/templates")


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
    model: str = Form(None),
    prompt: str = Form(...),
    max_tokens: int = Form(DEFAULT_PARAMS["max_tokens"]),
    temperature: float = Form(DEFAULT_PARAMS["temperature"]),
    top_p: float = Form(DEFAULT_PARAMS["top_p"]),
    repeat_penalty: float = Form(DEFAULT_PARAMS["repeat_penalty"]),
):
    start = time.time()
    models = list_models()

    response_text, token_count = generate_response(
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
    prompt: str
    model: str | None = None
    max_tokens: int = DEFAULT_PARAMS["max_tokens"]
    temperature: float = DEFAULT_PARAMS["temperature"]
    top_p: float = DEFAULT_PARAMS["top_p"]
    repeat_penalty: float = DEFAULT_PARAMS["repeat_penalty"]


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
        response_text, token_count = generate_response(
            user_input=req.prompt,
            model_name=req.model,
            max_tokens=req.max_tokens,
            temperature=req.temperature,
            top_p=req.top_p,
            repeat_penalty=req.repeat_penalty,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    duration = round(time.time() - start, 3)
    return GenerateResponse(
        response=response_text,
        tokens=token_count,
        duration=duration,
    )
