"""
Models and health API endpoints
"""
import time
from fastapi import APIRouter
from typing import Dict, Any
from ..schemas.requests import ModelsResponse, ModelInfo


router = APIRouter()


class ModelsAPI:
    """Models API handler"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
    
    def list_models(self) -> ModelsResponse:
        """List available models"""
        models = []
        
        # Add auto routing option
        models.append(ModelInfo(
            id="auto",
            owned_by="schitzo-router",
            description="Smart routing — classifies and picks the best model"
        ))
        
        # Add configured models
        model_registry = self.config.get("models", {})
        for model_id, model_config in model_registry.items():
            models.append(ModelInfo(
                id=model_id,
                owned_by=model_config.get("provider", "unknown"),
                description=f"Tier: {model_config.get('tier', 'unknown')}"
            ))
        
        return ModelsResponse(data=models)


class HealthAPI:
    """Health API handler"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.start_time = time.time()
    
    def health_check(self) -> Dict[str, Any]:
        """Basic health check"""
        return {
            "status": "ok",
            "service": "schitzo-neural-router",
            "version": "1.0.0"
        }
    
    def detailed_status(self) -> Dict[str, Any]:
        """Detailed status information"""
        import time
        
        uptime_seconds = int(time.time() - self.start_time)
        
        return {
            "status": "running",
            "classifier": {
                "model": self.config.get("classifier", {}).get("model", "unknown"),
                "status": "ready"  # TODO: Actually check Ollama status
            },
            "models": {
                "chat": self.config.get("routing", {}).get("chat_default", "unknown"),
                "low": self.config.get("routing", {}).get("low_default", "unknown"),
                "high": self.config.get("routing", {}).get("high_default", "unknown")
            },
            "uptime_seconds": uptime_seconds
        }


def create_models_router(config: Dict[str, Any]) -> APIRouter:
    """Create models router"""
    api = ModelsAPI(config)
    
    @router.get("/v1/models")
    def list_models():
        return api.list_models()
    
    return router


def create_health_router(config: Dict[str, Any]) -> APIRouter:
    """Create health router"""
    import time
    api = HealthAPI(config)
    
    @router.get("/health")
    def health_check():
        return api.health_check()
    
    @router.get("/status")
    def status():
        return api.detailed_status()
    
    return router