"""
Tracer interface for domain layer
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class TraceContext:
    """Context for a trace"""
    def __init__(self, trace_id: str, session_id: str):
        self.trace_id = trace_id
        self.session_id = session_id


class ITracer(ABC):
    """Interface for tracing requests"""
    
    @abstractmethod
    def start_trace(self, request_id: str, session_id: str) -> TraceContext:
        """Start a new trace"""
        pass
    
    @abstractmethod
    def add_span(self, trace_ctx: TraceContext, name: str, data: Dict[str, Any]) -> None:
        """Add a span to the trace"""
        pass
    
    @abstractmethod
    def end_trace(self, trace_ctx: TraceContext) -> None:
        """End the trace"""
        pass


class IRepository(ABC):
    """Interface for data persistence"""
    
    @abstractmethod
    def log_request(self, request_id: str, model: str, tier: str, cost: float, latency: float) -> None:
        """Log a request"""
        pass
    
    @abstractmethod
    def get_stats(self) -> Dict[str, Any]:
        """Get aggregated statistics"""
        pass