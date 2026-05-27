"""
Dependency injection container
"""
from typing import Dict, Any
from .infrastructure.config_loader import load_config
from .infrastructure.ollama_classifier import OllamaClassifier
from .infrastructure.litellm_forwarder import LiteLLMForwarder
from .infrastructure.websocket_emitter import WebSocketEmitter
from .infrastructure.langfuse_tracer import LangfuseTracer
from .infrastructure.sqlite_repository import SQLiteRepository
from .infrastructure.prometheus_metrics import PrometheusMetrics
from .application.route_prompt import RoutePromptUseCase


class Container:
    """Dependency injection container"""
    
    def __init__(self, config_path: str = None):
        self.config = load_config(config_path)
        self._instances = {}
    
    def get_classifier(self) -> OllamaClassifier:
        """Get classifier instance"""
        if 'classifier' not in self._instances:
            classifier_config = self.config.get('classifier', {})
            self._instances['classifier'] = OllamaClassifier(
                ollama_url=classifier_config.get('ollama_url', 'http://localhost:11434'),
                model=classifier_config.get('model', 'qwen2.5:7b'),
                timeout_ms=classifier_config.get('timeout_ms', 2000)
            )
        return self._instances['classifier']
    
    def get_forwarder(self) -> LiteLLMForwarder:
        """Get forwarder instance"""
        if 'forwarder' not in self._instances:
            self._instances['forwarder'] = LiteLLMForwarder()
        return self._instances['forwarder']
    
    def get_event_emitter(self) -> WebSocketEmitter:
        """Get event emitter instance"""
        if 'event_emitter' not in self._instances:
            self._instances['event_emitter'] = WebSocketEmitter()
        return self._instances['event_emitter']
    
    def get_tracer(self) -> LangfuseTracer:
        """Get tracer instance"""
        if 'tracer' not in self._instances:
            self._instances['tracer'] = LangfuseTracer(self.config)
        return self._instances['tracer']
    
    def get_repository(self) -> SQLiteRepository:
        """Get repository instance"""
        if 'repository' not in self._instances:
            self._instances['repository'] = SQLiteRepository()
        return self._instances['repository']
    
    def get_metrics(self) -> PrometheusMetrics:
        """Get metrics instance"""
        if 'metrics' not in self._instances:
            self._instances['metrics'] = PrometheusMetrics()
        return self._instances['metrics']
    
    def get_route_prompt_use_case(self) -> RoutePromptUseCase:
        """Get main routing use case"""
        if 'route_prompt_use_case' not in self._instances:
            self._instances['route_prompt_use_case'] = RoutePromptUseCase(
                classifier=self.get_classifier(),
                forwarder=self.get_forwarder(),
                event_emitter=self.get_event_emitter(),
                config=self.config
            )
        return self._instances['route_prompt_use_case']
    
    def get_config(self) -> Dict[str, Any]:
        """Get configuration"""
        return self.config