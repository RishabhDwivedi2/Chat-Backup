# app/services/agents/title_generator.py

from app.services.gpt_service import GPTService
from typing import Dict, Any, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

class TitleGenerator:
    """Agent responsible for generating dynamic titles for new chat collections."""

    def __init__(self, gpt_service: GPTService):
        self.gpt_service = gpt_service

    async def generate_unique_title(self, query: str, existing_titles: list, conversation_history: list = None, max_attempts: int = 3) -> Tuple[str, bool]:
        """
        Generate a unique title, retrying if conflicts occur.
        Returns tuple of (title, is_fallback) where is_fallback indicates if we had to use fallback generation.
        """
        attempt = 0
        used_titles = []
        
        while attempt < max_attempts:
            if attempt == 0:
                title = await self.generate_title(query, conversation_history)
            else:
                # For subsequent attempts, explicitly ask for a different title
                avoid_titles = ", ".join([f"'{t}'" for t in used_titles])
                title = await self.generate_title(
                    query,
                    conversation_history,
                    f"Please generate a different title than: {avoid_titles}"
                )
            
            if title not in existing_titles:
                return title, False
                
            used_titles.append(title)
            attempt += 1
            logger.info(f"Title '{title}' already exists, attempting regeneration (attempt {attempt}/{max_attempts})")
        
        # If we exhaust our attempts, create a uniquified fallback title
        fallback = self.generate_fallback_title(query, existing_titles)
        return fallback, True

    async def generate_title(self, query: str, conversation_history: list = None, avoid_prompt: str = "") -> str:
        """Generate a title for a new chat collection based on the initial query."""
        base_prompt = f"""Generate a short, concise title (maximum 5-6 words) for this conversation:
        Current query: '{query}'
        
        The title should be descriptive and relevant to the main topic.
        Return only the title without quotes or additional text."""
        
        if avoid_prompt:
            base_prompt = f"{base_prompt}\n{avoid_prompt}"
        
        try:
            title = await self.gpt_service.get_chat_response(
                prompt=base_prompt,
                max_tokens=20,
                temperature=0.7
            )
            return title.strip().strip('"\'')[:100]
        except Exception as e:
            logger.error(f"Error generating title: {str(e)}")
            return self.generate_fallback_title(query, [])

    def generate_fallback_title(self, query: str, existing_titles: list) -> str:
        """Generate a unique fallback title if title generation fails."""
        words = query.split()[:6]
        base_title = ' '.join(words)
        
        if len(base_title) > 100:
            base_title = f"{base_title[:97]}..."
            
        # If the base title is unique, use it
        if base_title not in existing_titles:
            return base_title
            
        # Otherwise, append a number until we get a unique title
        counter = 1
        while True:
            numbered_title = f"{base_title} ({counter})"
            if numbered_title not in existing_titles:
                return numbered_title
            counter += 1

    async def process(self, *args, **kwargs) -> Dict[str, Any]:
        """Dummy process method to satisfy BaseAgent inheritance."""
        return {}