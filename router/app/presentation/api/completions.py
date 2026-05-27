"""
Chat completions API endpoint
"""
import time
import uuid
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from typing import Dict, Any
from ..schemas.requests import CompletionRequest, CompletionResponse
from ...application.route_prompt import RoutePromptUseCase


router = APIRouter()


class CompletionsAPI:
    """Chat completions API handler"""
    
    def __init__(self, route_prompt_use_case: RoutePromptUseCase):
        self.route_prompt_use_case = route_prompt_use_case
    
    async def create_completion(self, request: CompletionRequest) -> Dict[str, Any]:
        """Handle chat completion request"""
        try:
            # Generate session ID (in real implementation, this would come from auth/headers)
            session_id = str(uuid.uuid4())
            
            # Convert Pydantic model to dict
            request_dict = request.model_dump()
            
            # Execute routing pipeline
            result = await self.route_prompt_use_case.execute(request_dict, session_id)
            
            # Handle streaming vs non-streaming
            if request.stream:
                return StreamingResponse(
                    self._stream_response(result),
                    media_type="text/plain"
                )
            else:
                # Add custom headers to response
                response_dict = dict(result)
                if "x_schitzo" not in response_dict:
                    response_dict["x_schitzo"] = {
                        "routing_method": "classify",
                        "tier": "unknown"
                    }
                
                return response_dict
                
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    async def _stream_response(self, stream_generator):
        """Convert async generator to SSE format"""
        try:
            async for chunk in stream_generator:
                # Format as SSE
                chunk_json = self._format_chunk(chunk)
                yield f"data: {chunk_json}\n\n"
            
            # Send final [DONE] message
            yield "data: [DONE]\n\n"
            
        except Exception as e:
            # Send error in SSE format
            error_chunk = {
                "error": {
                    "message": str(e),
                    "type": "routing_error"
                }
            }
            yield f"data: {error_chunk}\n\n"
    
    def _format_chunk(self, chunk: Dict[str, Any]) -> str:
        """Format chunk for SSE streaming"""
        import json
        return json.dumps(chunk, separators=(',', ':'))


def create_completions_router(route_prompt_use_case: RoutePromptUseCase) -> APIRouter:
    """Create completions router with dependency injection"""
    api = CompletionsAPI(route_prompt_use_case)
    
    @router.post("/v1/chat/completions")
    async def create_chat_completion(request: CompletionRequest):
        return await api.create_completion(request)
    
    return router