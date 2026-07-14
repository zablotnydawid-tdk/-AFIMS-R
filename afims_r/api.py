from __future__ import annotations
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Any
from .engine import run_validation

app = FastAPI(title="AFIMS-R", version="0.2.0")

class ValidationRequest(BaseModel):
    contract: dict[str, Any]
    source: dict[str, Any]
    answer: dict[str, Any]
    generator: dict[str, Any]

@app.get("/health")
def health() -> dict:
    return {"status": "ok", "version": "0.2.0"}

@app.post("/v1/validate")
def validate(request: ValidationRequest) -> dict:
    try:
        return run_validation(request.model_dump())
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
