# app/services/agents/base_agent.py

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from app.services.gpt_service import GPTService

class BaseAgent(ABC):
    """Base class for all agents"""
    
    def __init__(self, gpt_service: GPTService):
        self.gpt_service = gpt_service

    @abstractmethod
    async def process(self, *args, **kwargs) -> Dict[str, Any]:
        """Process the input and return results"""
        pass