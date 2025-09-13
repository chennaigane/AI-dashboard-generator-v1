from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.routers import analyze, health

import os

def get_allowed_origins():
    env = os.getenv("ALLOWED_ORIGINS", "")
    if not env:
        return ["*"]
    return [x.strip() for x in env.split(",") if x.strip()]

app = FastAPI(title="Automated Dashboard Generator & Insights Provider (Micro SaaS)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_allowed_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/api/health", tags=["health"])
app.include_router(analyze.router, prefix="/api/analyze", tags=["analyze"])
