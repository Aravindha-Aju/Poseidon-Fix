# -*- coding: utf-8 -*-
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.routes import pipeline

app = FastAPI(title="Poseidon API", description="AI-Based Oil Spill Detection & Vessel Source Attribution System", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.include_router(pipeline.router, prefix="/api/v1/pipeline", tags=["Pipeline"])

@app.get("/")
def read_root():
    return {"status": "Poseidon Backend is running.", "message": "Welcome to the Indian Ocean surveillance grid.", "docs": "/docs"}

