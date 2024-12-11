# app/services/gpt_service.py

import os
from typing import Dict, Any
import requests
import logging

logger = logging.getLogger(__name__)

class GPTService:
    def __init__(self):
        self.api_key = "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"
        self.api_url = "https://api.openai.com/v1/chat/completions" 
        
    async def get_chat_response(
        self, 
        prompt: str, 
        conversation_history: list = None,
        max_tokens: int = 100, 
        temperature: float = 0.7
    ) -> str:
        try:
            messages = []
            
            messages.append({
                "role": "system",
                "content": "You are a helpful assistant. Maintain context of the conversation and provide relevant responses."
            })
            
            # Add conversation history if available
            if conversation_history:
                for msg in conversation_history:
                    messages.append({
                        "role": msg["role"],
                        "content": msg["content"]
                    })
            
            # Add current prompt
            messages.append({
                "role": "user",
                "content": prompt
            })
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": "gpt-4o-mini",
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": temperature
            }
            
            logger.debug(f"Sending request to OpenAI API with payload: {payload}")
            
            response = requests.post(self.api_url, headers=headers, json=payload)
            response.raise_for_status()
            
            result = response.json()
            logger.debug(f"Received response from OpenAI API: {result}")
            
            return result["choices"][0]["message"]["content"].strip()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error calling GPT API: {str(e)}")
            if hasattr(e.response, 'json'):
                logger.error(f"API error details: {e.response.json()}")
            raise Exception(f"Failed to get response from GPT service: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error in GPT service: {str(e)}")
            raise