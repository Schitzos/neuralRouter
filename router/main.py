#!/usr/bin/env python3
"""Schitzo Neural Router - Main entry point."""

from fastapi import FastAPI

app = FastAPI(
    title="Schitzo Neural Router",
    description="Neural router for LLM model selection and routing",
    version="0.1.0"
)

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)