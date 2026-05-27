"""
Classifier interface for domain layer
"""
from abc import ABC, abstractmethod
from typing import Optional
from ..entities import Tier


class IClassifier(ABC):
    """Interface for prompt classification"""
    
    @abstractmethod
    async def classify(self, prompt: str, context_hint: str) -> Tier:
        """
        Classify a prompt into a tier
        
        Args:
            prompt: The user prompt to classify
            context_hint: Additional context (turn count, tools, etc.)
            
        Returns:
            Tier classification result
            
        Raises:
            ClassificationError: If classification fails
        """
        pass