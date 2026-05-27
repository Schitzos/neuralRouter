"""
Domain entities for Schitzo Neural Router
"""
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any


class Tier(Enum):
    """Model tier classification"""
    CHAT = "chat"
    LOW = "low"
    HIGH = "high"


@dataclass
class RouteDecision:
    """Routing decision result"""
    tier: Tier
    target_model: str
    method: str  # "classify" | "bypass"
    classification_latency_ms: Optional[float] = None


@dataclass
class CompletionRequest:
    """Domain representation of a completion request"""
    messages: List[Dict[str, Any]]
    model: Optional[str]
    stream: bool = False
    tools: Optional[List[Dict[str, Any]]] = None
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    raw_payload: Optional[Dict[str, Any]] = None


@dataclass
class RouterEvent:
    """Event emitted during routing pipeline"""
    id: str
    session_id: str
    request_id: str
    event_type: str
    timestamp: datetime
    data: Dict[str, Any]


class ClassificationError(Exception):
    """Raised when prompt classification fails"""
    pass


class ForwardingError(Exception):
    """Raised when request forwarding fails"""
    pass


class AllModelsFailedError(Exception):
    """Raised when all models in fallback chain fail"""
    pass