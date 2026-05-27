"""
Bypass detection use case
"""
from typing import Optional, Dict, Any


class DetectBypassUseCase:
    """Use case for detecting bypass keywords in user messages"""
    
    def __init__(self, bypass_patterns: Dict[str, str]):
        """
        Initialize with bypass patterns
        
        Args:
            bypass_patterns: Dict mapping patterns to model names
        """
        self.bypass_patterns = bypass_patterns
    
    def execute(self, user_message: str) -> Optional[str]:
        """
        Detect bypass keywords in user message
        
        Args:
            user_message: The user's message content
            
        Returns:
            Target model name if bypass detected, None otherwise
        """
        if not user_message:
            return None
            
        # Convert to lowercase for case-insensitive matching
        message_lower = user_message.lower().strip()
        
        # Check each bypass pattern
        for pattern, target_model in self.bypass_patterns.items():
            pattern_lower = pattern.lower()
            
            # Check if message starts with the pattern
            if message_lower.startswith(pattern_lower):
                return target_model
                
        return None