"""
Forwarder interface for domain layer
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, AsyncGenerator


class IForwarder(ABC):
    """Interface for request forwarding to models"""
    
    @abstractmethod
    async def forward(self, request: Dict[str, Any], model: str) -> Dict[str, Any]:
        """
        Forward a request to a model
        
        Args:
            request: The request payload
            model: Target model identifier
            
        Returns:
            Response from the model
            
        Raises:
            ForwardingError: If forwarding fails
        """
        pass
    
    @abstractmethod
    async def forward_stream(self, request: Dict[str, Any], model: str) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Forward a streaming request to a model
        
        Args:
            request: The request payload
            model: Target model identifier
            
        Yields:
            Streaming response chunks
            
        Raises:
            ForwardingError: If forwarding fails
        """
        pass