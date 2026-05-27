"""
Langfuse tracer implementation
"""
import os
from typing import Dict, Any, Optional
from langfuse import Langfuse
from ..domain.interfaces.tracer import ITracer, TraceContext


class LangfuseTracer(ITracer):
    """Langfuse-based tracer for request tracking"""
    
    def __init__(self, config: Dict[str, Any]):
        langfuse_config = config.get("observability", {}).get("langfuse", {})
        
        if langfuse_config.get("enabled", False):
            self.client = Langfuse(
                public_key=os.getenv("LANGFUSE_PUBLIC_KEY", ""),
                secret_key=os.getenv("LANGFUSE_SECRET_KEY", ""),
                host=os.getenv("LANGFUSE_HOST", "http://localhost:3000")
            )
            self.enabled = True
        else:
            self.client = None
            self.enabled = False
    
    def start_trace(self, request_id: str, session_id: str) -> TraceContext:
        """Start a new trace"""
        trace_ctx = TraceContext(request_id, session_id)
        
        if self.enabled and self.client:
            try:
                trace_ctx.langfuse_trace = self.client.trace(
                    id=request_id,
                    session_id=session_id,
                    name="chat_completion"
                )
            except Exception as e:
                print(f"Failed to start Langfuse trace: {e}")
        
        return trace_ctx
    
    def add_span(self, trace_ctx: TraceContext, name: str, data: Dict[str, Any]) -> None:
        """Add a span to the trace"""
        if not self.enabled or not hasattr(trace_ctx, 'langfuse_trace'):
            return
            
        try:
            if name == "llm_call":
                # Create generation span for LLM calls
                trace_ctx.langfuse_trace.generation(
                    name=name,
                    model=data.get("model"),
                    input=data.get("input"),
                    output=data.get("output"),
                    usage=data.get("usage"),
                    metadata=data.get("metadata", {})
                )
            else:
                # Create regular span
                trace_ctx.langfuse_trace.span(
                    name=name,
                    input=data.get("input"),
                    output=data.get("output"),
                    metadata=data.get("metadata", {})
                )
        except Exception as e:
            print(f"Failed to add Langfuse span: {e}")
    
    def end_trace(self, trace_ctx: TraceContext) -> None:
        """End the trace"""
        if self.enabled and hasattr(trace_ctx, 'langfuse_trace'):
            try:
                # Langfuse traces are automatically finalized
                pass
            except Exception as e:
                print(f"Failed to end Langfuse trace: {e}")