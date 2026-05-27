"""
Classify prompt use case
"""
from typing import List, Dict, Any
from ..domain.interfaces.classifier import IClassifier
from ..domain.entities import Tier


class ClassifyPromptUseCase:
    """Use case for classifying prompts"""
    
    def __init__(self, classifier: IClassifier):
        self.classifier = classifier
    
    async def execute(self, messages: List[Dict[str, Any]], tools: List[Dict[str, Any]] = None) -> Tier:
        """
        Classify a prompt based on messages and context
        
        Args:
            messages: List of conversation messages
            tools: Optional list of available tools
            
        Returns:
            Tier classification
        """
        # Extract last user message
        last_user_message = self._extract_last_user_message(messages)
        
        if not last_user_message:
            # No user message, default to HIGH
            return Tier.HIGH
            
        # Build context hint
        context_hint = self._build_context_hint(messages, tools)
        
        # Classify using the classifier
        tier = await self.classifier.classify(last_user_message, context_hint)
        
        return tier
    
    def _extract_last_user_message(self, messages: List[Dict[str, Any]]) -> str:
        """Extract the last user message from the conversation"""
        for message in reversed(messages):
            if message.get("role") == "user":
                content = message.get("content", "")
                if isinstance(content, str):
                    return content.strip()
                elif isinstance(content, list):
                    # Handle multi-modal content
                    text_parts = [part.get("text", "") for part in content if part.get("type") == "text"]
                    return " ".join(text_parts).strip()
        
        return ""
    
    def _build_context_hint(self, messages: List[Dict[str, Any]], tools: List[Dict[str, Any]] = None) -> str:
        """Build context hint for classification"""
        hints = []
        
        # Turn count
        turn_count = len([m for m in messages if m.get("role") == "user"])
        hints.append(f"This is turn {turn_count} of a conversation")
        
        # Tools presence
        if tools:
            hints.append(f"Tools available: {len(tools)} tools")
        else:
            hints.append("No tools available")
            
        # Check for code blocks in recent messages
        recent_messages = messages[-3:] if len(messages) > 3 else messages
        has_code = any("```" in str(msg.get("content", "")) for msg in recent_messages)
        if has_code:
            hints.append("Recent code discussion")
            
        return ". ".join(hints) + "."