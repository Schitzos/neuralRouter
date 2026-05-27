"""
Main route prompt use case - orchestrates the entire routing pipeline
"""
import time
import uuid
from datetime import datetime
from typing import Dict, Any, AsyncGenerator, Union
from ..domain.entities import Tier, RouteDecision, RouterEvent, AllModelsFailedError
from ..domain.interfaces.classifier import IClassifier
from ..domain.interfaces.forwarder import IForwarder
from ..domain.interfaces.event_emitter import IEventEmitter
from .detect_bypass import DetectBypassUseCase
from .classify_prompt import ClassifyPromptUseCase


class RoutePromptUseCase:
    """Main orchestrator for the routing pipeline"""
    
    def __init__(
        self,
        classifier: IClassifier,
        forwarder: IForwarder,
        event_emitter: IEventEmitter,
        config: Dict[str, Any]
    ):
        self.classifier = classifier
        self.forwarder = forwarder
        self.event_emitter = event_emitter
        self.config = config
        
        # Initialize sub-use cases
        self.bypass_detector = DetectBypassUseCase(config.get("bypass", {}))
        self.prompt_classifier = ClassifyPromptUseCase(classifier)
    
    async def execute(
        self, 
        request: Dict[str, Any], 
        session_id: str
    ) -> Union[Dict[str, Any], AsyncGenerator[Dict[str, Any], None]]:
        """
        Execute the complete routing pipeline
        
        Args:
            request: The incoming request payload
            session_id: Session identifier for tracking
            
        Returns:
            Response dict or async generator for streaming
        """
        request_id = str(uuid.uuid4())
        start_time = time.time()
        
        # Emit request start event
        await self._emit_event("request_start", request_id, session_id, {
            "message_preview": self._get_message_preview(request),
            "stream": request.get("stream", False),
            "has_tools": bool(request.get("tools"))
        })
        
        try:
            # Step 1: Bypass detection
            route_decision = await self._detect_bypass(request, request_id, session_id)
            
            # Step 2: Classification (if no bypass)
            if route_decision is None:
                route_decision = await self._classify_request(request, request_id, session_id)
            
            # Step 3: Forward to model
            if request.get("stream", False):
                return self._forward_stream(request, route_decision, request_id, session_id)
            else:
                return await self._forward_request(request, route_decision, request_id, session_id)
                
        except Exception as e:
            await self._emit_event("request_error", request_id, session_id, {
                "error": str(e),
                "latency_ms": (time.time() - start_time) * 1000
            })
            raise
    
    async def _detect_bypass(self, request: Dict[str, Any], request_id: str, session_id: str) -> RouteDecision:
        """Detect bypass keywords"""
        messages = request.get("messages", [])
        if not messages:
            return None
            
        # Get last user message
        last_user_message = ""
        for message in reversed(messages):
            if message.get("role") == "user":
                last_user_message = str(message.get("content", ""))
                break
        
        # Check for bypass
        target_model = self.bypass_detector.execute(last_user_message)
        
        if target_model:
            await self._emit_event("bypass_detected", request_id, session_id, {
                "target_model": target_model,
                "keyword": self._find_bypass_keyword(last_user_message)
            })
            
            return RouteDecision(
                tier=Tier.HIGH,  # Bypass is typically for complex requests
                target_model=target_model,
                method="bypass"
            )
        
        return None
    
    async def _classify_request(self, request: Dict[str, Any], request_id: str, session_id: str) -> RouteDecision:
        """Classify the request and determine routing"""
        start_time = time.time()
        
        await self._emit_event("classify_start", request_id, session_id, {
            "input_preview": self._get_message_preview(request)
        })
        
        try:
            # Classify the prompt
            tier = await self.prompt_classifier.execute(
                request.get("messages", []),
                request.get("tools")
            )
            
            classification_latency = (time.time() - start_time) * 1000
            
            await self._emit_event("classify_complete", request_id, session_id, {
                "tier": tier.value,
                "latency_ms": classification_latency
            })
            
            # Resolve target model from tier
            target_model = self._resolve_model_from_tier(tier)
            
            await self._emit_event("route_decision", request_id, session_id, {
                "target_model": target_model,
                "tier": tier.value,
                "method": "classify"
            })
            
            return RouteDecision(
                tier=tier,
                target_model=target_model,
                method="classify",
                classification_latency_ms=classification_latency
            )
            
        except Exception as e:
            # Default to HIGH tier on classification failure
            target_model = self._resolve_model_from_tier(Tier.HIGH)
            
            await self._emit_event("classify_error", request_id, session_id, {
                "error": str(e),
                "fallback_tier": "high",
                "target_model": target_model
            })
            
            return RouteDecision(
                tier=Tier.HIGH,
                target_model=target_model,
                method="fallback"
            )
    
    async def _forward_request(
        self, 
        request: Dict[str, Any], 
        route_decision: RouteDecision, 
        request_id: str, 
        session_id: str
    ) -> Dict[str, Any]:
        """Forward non-streaming request"""
        start_time = time.time()
        
        await self._emit_event("forward_start", request_id, session_id, {
            "model": route_decision.target_model,
            "stream": False
        })
        
        # Try primary model first, then fallback chain
        fallback = self._get_fallback_chain(route_decision.tier)
        models_to_try = [route_decision.target_model] + [m for m in fallback if m != route_decision.target_model]
        
        for i, model in enumerate(models_to_try):
            try:
                # Update request with target model
                request_copy = request.copy()
                request_copy["model"] = model
                
                response = await self.forwarder.forward(request_copy, model)
                
                latency_ms = (time.time() - start_time) * 1000
                
                await self._emit_event("forward_complete", request_id, session_id, {
                    "model": model,
                    "latency_ms": latency_ms,
                    "status": "success"
                })
                
                # Add routing metadata
                response["x_schitzo"] = {
                    "routing_method": route_decision.method,
                    "tier": route_decision.tier.value,
                    "model": model,
                    "latency_ms": round(latency_ms, 2)
                }
                
                return response
                
            except Exception as e:
                if i < len(models_to_try) - 1:
                    # Try next model in fallback chain
                    next_model = models_to_try[i + 1]
                    await self._emit_event("fallback_triggered", request_id, session_id, {
                        "from_model": model,
                        "to_model": next_model,
                        "reason": str(e)
                    })
                else:
                    # All models failed
                    raise AllModelsFailedError(f"All models failed: {str(e)}")
    
    async def _forward_stream(
        self, 
        request: Dict[str, Any], 
        route_decision: RouteDecision, 
        request_id: str, 
        session_id: str
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Forward streaming request"""
        await self._emit_event("forward_start", request_id, session_id, {
            "model": route_decision.target_model,
            "stream": True
        })
        
        # Update request with target model
        request_copy = request.copy()
        request_copy["model"] = route_decision.target_model
        
        try:
            async for chunk in self.forwarder.forward_stream(request_copy, route_decision.target_model):
                yield chunk
                
            await self._emit_event("forward_complete", request_id, session_id, {
                "model": route_decision.target_model,
                "status": "success"
            })
            
        except Exception as e:
            await self._emit_event("forward_error", request_id, session_id, {
                "model": route_decision.target_model,
                "error": str(e)
            })
            raise
    
    def _resolve_model_from_tier(self, tier: Tier) -> str:
        """Resolve target model from tier"""
        routing_config = self.config.get("routing", {})
        
        if tier == Tier.CHAT:
            return routing_config.get("chat_default", "moonshot/moonshot-v1-8k")
        elif tier == Tier.LOW:
            return routing_config.get("low_default", "moonshot/moonshot-v1-8k")
        else:  # HIGH
            return routing_config.get("high_default", "moonshot/moonshot-v1-128k")
    
    def _get_fallback_chain(self, tier: Tier) -> list:
        """Get fallback chain for a tier"""
        fallback_config = self.config.get("fallback", {})
        
        if tier == Tier.LOW or tier == Tier.CHAT:
            return fallback_config.get("low", ["moonshot/moonshot-v1-8k"])
        else:  # HIGH
            return fallback_config.get("high", ["moonshot/moonshot-v1-128k"])
    
    def _get_message_preview(self, request: Dict[str, Any]) -> str:
        """Get a preview of the last user message"""
        messages = request.get("messages", [])
        for message in reversed(messages):
            if message.get("role") == "user":
                content = str(message.get("content", ""))
                return content[:100] + "..." if len(content) > 100 else content
        return ""
    
    def _find_bypass_keyword(self, message: str) -> str:
        """Find which bypass keyword was matched"""
        message_lower = message.lower()
        for pattern in self.config.get("bypass", {}):
            if message_lower.startswith(pattern.lower()):
                return pattern
        return ""
    
    async def _emit_event(self, event_type: str, request_id: str, session_id: str, data: Dict[str, Any]):
        """Emit a router event"""
        event = RouterEvent(
            id=str(uuid.uuid4()),
            session_id=session_id,
            request_id=request_id,
            event_type=event_type,
            timestamp=datetime.utcnow(),
            data=data
        )
        
        await self.event_emitter.emit(event)