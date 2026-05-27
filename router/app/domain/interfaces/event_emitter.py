"""
Event emitter interface for domain layer
"""
from abc import ABC, abstractmethod
from ..entities import RouterEvent


class IEventEmitter(ABC):
    """Interface for emitting router events"""
    
    @abstractmethod
    async def emit(self, event: RouterEvent) -> None:
        """
        Emit a router event
        
        Args:
            event: The event to emit
        """
        pass