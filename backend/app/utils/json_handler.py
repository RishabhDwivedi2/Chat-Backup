# app/utils/json_handler.py

from typing import Dict, Any, List
import json
import logging

logger = logging.getLogger(__name__)

class JSONHandler:
    """Helper class for robust JSON handling from GPT responses"""
    
    @staticmethod
    def extract_clean_json(response: str) -> Dict[str, Any]:
        """Extract and clean JSON from GPT response, handling markdown and formatting"""
        try:
            # Remove markdown code blocks and clean up
            cleaned = response.replace('```json', '')
            cleaned = cleaned.replace('```', '')
            cleaned = cleaned.strip()
            
            # Find JSON content
            start_idx = cleaned.find('{')
            end_idx = cleaned.rfind('}') + 1
            
            if start_idx != -1 and end_idx > 0:
                json_str = cleaned[start_idx:end_idx]
                # Parse and validate JSON
                parsed = json.loads(json_str)
                return parsed
            
            raise ValueError("No JSON content found")
            
        except Exception as e:
            logger.error(f"Error extracting JSON: {str(e)}")
            logger.debug(f"Original response: {response}")
            return {}

    @staticmethod
    def generate_json_prompt(prompt_text: str) -> str:
        """Generate a prompt that explicitly asks for clean JSON"""
        return f"""{prompt_text}

        REQUIREMENTS:
        1. Return ONLY valid JSON
        2. Start with {{ and end with }}
        3. NO markdown formatting
        4. NO explanatory text
        5. NO code blocks or ```
        6. Include ONLY the JSON object
        """

    @staticmethod
    def validate_json_structure(data: Dict[str, Any], required_fields: list = None) -> Dict[str, Any]:
        """Validate JSON structure and required fields"""
        try:
            # Test serialization
            json.dumps(data)
            
            # Check required fields if specified
            if required_fields:
                for field in required_fields:
                    if field not in data:
                        logger.warning(f"Missing required field: {field}")
                        data[field] = None
            
            return data
        except Exception as e:
            logger.error(f"Invalid JSON structure: {str(e)}")
            return {}