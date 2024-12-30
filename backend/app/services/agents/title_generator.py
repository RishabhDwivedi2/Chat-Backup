# app/services/agents/title_generator.py

from app.services.gpt_service import GPTService
from typing import Dict, Any, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

class TitleGenerator:
    """Agent responsible for generating dynamic titles for new chat collections."""

    def __init__(self, gpt_service: GPTService):
        self.gpt_service = gpt_service

    async def generate_unique_title(self, query: str, existing_titles: list = None, conversation_history: list = None, max_attempts: int = 3) -> Tuple[str, bool]:
        """
        Generate a title for the conversation.
        Returns tuple of (title, is_fallback) where is_fallback indicates if we had to use fallback generation.
        """
        try:
            title = await self.generate_title(query, conversation_history)
            return title, False
        except Exception as e:
            logger.error(f"Error generating title: {str(e)}")
            fallback = self.generate_fallback_title(query)
            return fallback, True

    async def generate_title(self, query: str, conversation_history: list = None, avoid_prompt: str = "") -> str:
        """Generate a title for a new chat collection based on the initial query."""
        base_prompt = f"""Generate a short, concise title (maximum 5-6 words) for this conversation:
        Current query: '{query}'
        
        The title should be descriptive and relevant to the main topic.
        Return only the title without quotes or additional text."""
        
        try:
            title = await self.gpt_service.get_chat_response(
                prompt=base_prompt,
                max_tokens=20,
                temperature=0.7
            )
            return title.strip().strip('"\'')[:100]
        except Exception as e:
            logger.error(f"Error generating title: {str(e)}")
            return self.generate_fallback_title(query)

    def generate_fallback_title(self, query: str) -> str:
        """Generate a fallback title if title generation fails."""
        words = query.split()[:6]
        base_title = ' '.join(words)
        
        if len(base_title) > 100:
            base_title = f"{base_title[:97]}..."
            
        return base_title

    async def process(self, *args, **kwargs) -> Dict[str, Any]:
        """Dummy process method to satisfy BaseAgent inheritance."""
        return {}