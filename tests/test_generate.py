# tests/test_generate.py
import asyncio

import httpx

from app.main import app


def post_generate(payload: dict):
    async def request():
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            return await client.post("/api/generate", json=payload)

    return asyncio.run(request())


def test_generate_endpoint(monkeypatch):
    async def run_in_test_thread(func, **kwargs):
        return func(**kwargs)

    monkeypatch.setattr("app.routes.generate.asyncio.to_thread", run_in_test_thread)
    monkeypatch.setattr(
        "app.routes.generate.generate_response",
        lambda **_: ("A generated response", 12),
    )
    prompt = "Розкажи мені щось цікаве про чорні діри"
    response = post_generate({"prompt": prompt})

    assert response.status_code == 200
    data = response.json()

    assert data["response"] == "A generated response"
    assert data["tokens"] == 12
    assert data["duration"] >= 0


def test_generate_rejects_invalid_parameters():
    response = post_generate({"prompt": "Hello", "max_tokens": 2049})

    assert response.status_code == 422


def test_generate_does_not_expose_internal_errors(monkeypatch):
    async def run_in_test_thread(func, **kwargs):
        return func(**kwargs)

    def fail(**_):
        raise RuntimeError("/private/path")

    monkeypatch.setattr("app.routes.generate.asyncio.to_thread", run_in_test_thread)
    monkeypatch.setattr("app.routes.generate.generate_response", fail)
    response = post_generate({"prompt": "Hello"})

    assert response.status_code == 500
    assert response.json() == {"detail": "Generation failed"}
