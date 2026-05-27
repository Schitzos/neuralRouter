"""
Schitzo Neural Router - Main FastAPI Application
"""
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .container import Container
from .presentation.api.completions import create_completions_router
from .presentation.api.models import create_models_router, create_health_router
from .presentation.api.websocket import create_websocket_router

# Initialize container
container = Container()
config = container.get_config()

app = FastAPI(
    title="Schitzo Neural Router",
    description="AI Model Routing Proxy with Real-Time Observability",
    version="1.0.0"
)

# CORS middleware for dashboard
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3001"],  # Dashboard URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(create_completions_router(container.get_route_prompt_use_case()))
app.include_router(create_models_router(config))
app.include_router(create_health_router(config))
app.include_router(create_websocket_router(container.get_event_emitter()))

# Metrics endpoint
@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    return container.get_metrics().get_metrics()

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Schitzo Neural Router API", "version": "1.0.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)