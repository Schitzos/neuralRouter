"""
LiteLLM forwarder implementation
"""
import os
import litellm
from typing import Dict, Any, AsyncGenerator
from ..domain.interfaces.forwarder import IForwarder
from ..domain.entities import ForwardingError


class LiteLLMForwarder(IForwarder):
    """Forwarder using LiteLLM for model requests"""
    
    def __init__(self):
        # Configure LiteLLM
        litellm.set_verbose = False
        
        # Enable Langfuse callback if keys are set
        if os.getenv("LANGFUSE_PUBLIC_KEY") and os.getenv("LANGFUSE_SECRET_KEY"):
            litellm.success_callback = ["langfuse"]
            litellm.failure_callback = ["langfuse"]
        
    async def forward(self, request: Dict[str, Any], model: str) -> Dict[str, Any]:
        """Forward non-streaming request to model"""
        try:
            # Prepare request for LiteLLM
            litellm_request = self._prepare_request(request, model)
            
            # Make the request
            response = await litellm.acompletion(**litellm_request)
            
            # Convert response to dict
            return response.model_dump() if hasattr(response, 'model_dump') else dict(response)
            
        except Exception as e:
            raise ForwardingError(f"Failed to forward request to {model}: {str(e)}")
    
    async def forward_stream(self, request: Dict[str, Any], model: str) -> AsyncGenerator[Dict[str, Any], None]:
        """Forward streaming request to model"""
        try:
            # Prepare request for LiteLLM
            litellm_request = self._prepare_request(request, model, stream=True)
            
            # Make streaming request
            response = await litellm.acompletion(**litellm_request)
            
            # Yield chunks
            async for chunk in response:
                chunk_dict = chunk.model_dump() if hasattr(chunk, 'model_dump') else dict(chunk)
                yield chunk_dict
                
        except Exception as e:
            raise ForwardingError(f"Failed to forward streaming request to {model}: {str(e)}")
    
    def _prepare_request(self, request: Dict[str, Any], model: str, stream: bool = False) -> Dict[str, Any]:
        """Prepare request for LiteLLM"""
        litellm_request = {
            "model": model,
            "messages": request.get("messages", []),
            "stream": stream or request.get("stream", False),
            "timeout": 60
        }
        
        # Add optional parameters
        optional_params = [
            "temperature", "max_tokens", "top_p", "frequency_penalty", 
            "presence_penalty", "stop", "tools", "tool_choice"
        ]
        
        for param in optional_params:
            if param in request:
                litellm_request[param] = request[param]
        
        return litellm_request