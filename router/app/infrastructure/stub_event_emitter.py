"""
Stub event emitter for Phase 1 testing
"""
from ..domain.interfaces.event_emitter import IEventEmitter
from ..domain.entities import RouterEvent


class StubEventEmitter(IEventEmitter):
    """Stub implementation for testing Phase 1"""
    
    def __init__(self):
        self.events = []
    
    async def emit(self, event: RouterEvent) -> None:
        """Store event for testing"""
        self.events.append(event)
        print(f"Event: {event.event_type} - {event.data}")  # Simple logging