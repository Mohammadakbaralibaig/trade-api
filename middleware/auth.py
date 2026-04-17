import os
from fastapi import Request, HTTPException
from dotenv import load_dotenv

load_dotenv()

API_SECRET_KEY = os.getenv("API_SECRET_KEY", "mysecretkey123")

async def verify_api_key(request: Request):
    api_key = request.headers.get("X-API-Key")
    if not api_key or api_key != API_SECRET_KEY:
        raise HTTPException(status_code=403, detail="Invalid or missing API Key")