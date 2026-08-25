# app/routes/ping.py
from fastapi import APIRouter

router = APIRouter()

@router.get("/ping")
async def ping():
    print("/ping called")
    return {"status": "ok"}
