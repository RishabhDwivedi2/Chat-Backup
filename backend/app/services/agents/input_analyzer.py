# app/services/agents/input_analyzer.py

from typing import Dict, Any, List, Optional
import logging
from datetime import datetime
import mimetypes
from pathlib import Path
from app.services.gpt_service import GPTService
import json
from app.utils.json_handler import JSONHandler

logger = logging.getLogger(__name__)


class InputAnalyzer:
    def __init__(self, gpt_service: GPTService):
        self.gpt_service = gpt_service
        self.supported_file_types = {
            'document': ['.pdf', '.doc', '.docx', '.txt', '.rtf'],
            'image': ['.jpg', '.jpeg', '.png', '.gif', '.bmp'],
            'audio': ['.mp3', '.wav', '.ogg', '.m4a'],
            'spreadsheet': ['.xlsx', '.xls', '.csv'],
            'presentation': ['.ppt', '.pptx']
        }
        self.system_prompt = """You are an Input Analysis Agent. Your role is to:
            1. Analyze user queries and their attachments in the context of the conversation
            2. Identify the type and characteristics of each attachment
            3. Determine necessary processing steps for different file types
            4. Consider conversation history for contextual understanding
            5. Provide a detailed metadata analysis in a structured JSON format

            Respond with a detailed JSON metadata following this structure:
            {
                "metadata": {
                    "analysis": "Brief summary of user query considering context",
                    "has_attachments": boolean,
                    "attachments": ["list of attachment names"],
                    "context_summary": "Brief summary of relevant context from conversation"
                }
            }"""

    async def analyze_input(
        self,
        query: str,
        attachments: Optional[List[Dict[str, Any]]] = None,
        conversation_history: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Analyze the input query and attachments using GPT and return analysis with metadata
        
        Args:
            query (str): The current user query
            attachments (Optional[List[Dict[str, Any]]]): List of attachment metadata
            conversation_history (Optional[List[Dict[str, Any]]]): Previous conversation messages
        """
        try:
            # Construct prompt for GPT
            analysis_prompt = self._construct_analysis_prompt(query, attachments, conversation_history)
            
            # Get GPT's analysis
            gpt_response = await self.gpt_service.get_chat_response(
                prompt=analysis_prompt,
                max_tokens=1000,
                temperature=0.2
            )

            # Use JSONHandler for parsing
            gpt_analysis = JSONHandler.extract_clean_json(gpt_response)

            # Generate metadata for logging and response
            metadata = self._generate_metadata(gpt_analysis, query, attachments, conversation_history)

            # Combine analysis and metadata for final output
            return {
                "input_analysis": gpt_analysis,
                "metadata": metadata
            }

        except Exception as e:
            logger.error(f"Error in input analysis: {str(e)}", exc_info=True)
            raise


    def _generate_metadata(
        self,
        gpt_analysis: Dict[str, Any],
        query: str,
        attachments: Optional[List[Dict[str, Any]]] = None,
        conversation_history: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """Generate structured metadata based on analysis and context"""

        metadata = {
            "analysis": gpt_analysis.get("analysis", "No analysis available"),
            "has_attachments": bool(attachments),
            "attachments": [Path(att["file_path"]).name for att in attachments] if attachments else [],
            "context_summary": self._summarize_context(conversation_history) if conversation_history else "No prior context"
        }
        return metadata

    def _construct_analysis_prompt(
        self,
        query: str,
        attachments: Optional[List[Dict[str, Any]]] = None,
        conversation_history: Optional[List[Dict[str, Any]]] = None
    ) -> str:
        """Construct the prompt for GPT analysis including conversation context"""

        # Build attachment information
        attachment_info = []
        if attachments:
            for att in attachments:
                file_ext = Path(att.get("file_path", "")).suffix.lower()
                file_type = self._get_attachment_type(file_ext)
                size = att.get("file_size", 0)
                attachment_info.append(f"- {Path(att['file_path']).name}: {file_type} file, size: {size} bytes")

        # Build context information
        context_info = []
        if conversation_history:
            for msg in conversation_history[-5:]:  # Include last 5 messages for context
                role = msg.get("role", "unknown")
                content = msg.get("content", "")
                context_info.append(f"{role}: {content}")

        prompt = f"""Analyze the following user input with conversation context:

                CONVERSATION HISTORY:
                {chr(10).join(context_info) if context_info else "No prior conversation"}

                CURRENT QUERY:
                {query}

                ATTACHMENTS PRESENT: {bool(attachments)}
                {f'ATTACHMENT DETAILS:\\n' + '\\n'.join(attachment_info) if attachments else 'NO ATTACHMENTS'}

                Please provide a JSON response that includes:
                1. Analysis of the query in context of the conversation
                2. Metadata with the following structure:
                - "analysis": Brief summary of the user query considering context
                - "has_attachments": boolean
                - "attachments": ["list of attachment names"]
                - "context_summary": Brief summary of relevant context from conversation
                """
        return prompt

    def _summarize_context(self, conversation_history: Optional[List[Dict[str, Any]]]) -> str:
        """Generate a brief summary of the conversation context"""
        if not conversation_history:
            return "No prior context"
            
        # Take the last few messages for context summary
        recent_messages = conversation_history[-5:]
        context_summary = []
        
        for msg in recent_messages:
            role = msg.get("role", "unknown")
            content = msg.get("content", "")
            context_summary.append(f"{role}: {content}")
            
        return " → ".join(context_summary)

    def _get_attachment_type(self, file_ext: str) -> str:
        """Get attachment type from extension"""
        for file_type, extensions in self.supported_file_types.items():
            if file_ext in extensions:
                return file_type
        return "unknown"

    def _extract_json_from_text(self, text: str) -> Dict[str, Any]:
        """Extract JSON from GPT response if not properly formatted"""
        try:
            start_idx = text.find('{')
            end_idx = text.rfind('}') + 1
            if start_idx != -1 and end_idx != 0:
                json_str = text[start_idx:end_idx]
                return json.loads(json_str)
        except Exception:
            pass

        return {
            "analysis": "Failed to parse response",
            "has_attachments": False,
            "attachments": [],
            "context_summary": "No context available"
        }