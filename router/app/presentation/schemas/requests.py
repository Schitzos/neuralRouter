"""
Pydantic schemas for API requests and responses
"""
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Union


class Message(BaseModel):
    """Chat message schema"""
    role: str
    content: Union[str, List[Dict[str, Any]]]
    name: Optional[str] = None


class CompletionRequest(BaseModel):
    """Chat completion request schema"""
    model: str = "auto"
    messages: List[Message]
    temperature: Optional[float] = Field(None, ge=0, le=2)
    max_tokens: Optional[int] = Field(None, gt=0)
    top_p: Optional[float] = Field(None, ge=0, le=1)
    frequency_penalty: Optional[float] = Field(None, ge=-2, le=2)
    presence_penalty: Optional[float] = Field(None, ge=-2, le=2)
    stop: Optional[Union[str, List[str]]] = None
    stream: Optional[bool] = False
    tools: Optional[List[Dict[str, Any]]] = None
    tool_choice: Optional[Union[str, Dict[str, Any]]] = None


class Choice(BaseModel):
    """Response choice schema"""
    index: int
    message: Optional[Message] = None
    delta: Optional[Dict[str, Any]] = None
    finish_reason: Optional[str] = None


class Usage(BaseModel):
    """Token usage schema"""
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


class CompletionResponse(BaseModel):
    """Chat completion response schema"""
    id: str
    object: str = "chat.completion"
    created: int
    model: str
    choices: List[Choice]
    usage: Optional[Usage] = None


class ModelInfo(BaseModel):
    """Model information schema"""
    id: str
    object: str = "model"
    owned_by: str
    description: Optional[str] = None


class ModelsResponse(BaseModel):
    """Models list response schema"""
    object: str = "list"
    data: List[ModelInfo]