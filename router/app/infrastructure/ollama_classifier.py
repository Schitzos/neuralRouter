"""
Ollama classifier implementation
"""
import asyncio
import httpx
import json
import time
from typing import Dict, Any
from ..domain.interfaces.classifier import IClassifier
from ..domain.entities import Tier, ClassificationError


class OllamaClassifier(IClassifier):
    """Classifier using Ollama/Qwen 2.5 7B"""
    
    def __init__(self, ollama_url: str, model: str, timeout_ms: int = 2000):
        self.ollama_url = ollama_url
        self.model = model
        self.timeout_ms = timeout_ms
        
    async def classify(self, prompt: str, context_hint: str) -> Tier:
        """Classify prompt using Qwen 2.5 7B via Ollama"""
        
        # Build classification prompt
        classification_prompt = self._build_classification_prompt(prompt, context_hint)
        
        start_time = time.time()
        
        try:
            # Call Ollama API
            async with httpx.AsyncClient(timeout=self.timeout_ms / 1000) as client:
                response = await client.post(
                    f"{self.ollama_url}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": classification_prompt,
                        "stream": False,
                        "options": {
                            "temperature": 0.1,
                            "top_p": 0.9,
                            "num_predict": 10  # We only need a short response
                        }
                    }
                )
                
            if response.status_code != 200:
                raise ClassificationError(f"Ollama API error: {response.status_code}")
                
            result = response.json()
            classification_text = result.get("response", "").strip().lower()
            
            # Parse classification result
            tier = self._parse_classification(classification_text)
            
            return tier
            
        except asyncio.TimeoutError:
            raise ClassificationError("Classification timeout")
        except Exception as e:
            raise ClassificationError(f"Classification failed: {str(e)}")
    
    def _build_classification_prompt(self, prompt: str, context_hint: str) -> str:
        """Build the classification prompt for Qwen"""
        return f'''System: You are a prompt complexity classifier. Classify the user's prompt into one of three categories: "chat", "low", or "high".

"chat" = casual conversation, greetings, small talk, confirmations, emoji reactions, "hi", "thanks", "ok", "yes", "no", "how are you", chit-chat with no task
"low" = simple questions, formatting, translation, short factual answers, single-step tasks, lookups
"high" = complex reasoning, architecture design, multi-step analysis, code generation, debugging, creative writing, planning

Context: {context_hint}

Respond with ONLY "chat", "low", or "high".

User: {prompt}'''
    
    def _parse_classification(self, classification_text: str) -> Tier:
        """Parse classification result from model response"""
        # Clean up the response
        classification_text = classification_text.strip().lower()
        
        # Extract the classification
        if "chat" in classification_text:
            return Tier.CHAT
        elif "low" in classification_text:
            return Tier.LOW
        elif "high" in classification_text:
            return Tier.HIGH
        else:
            # Default to HIGH if unclear
            return Tier.HIGH