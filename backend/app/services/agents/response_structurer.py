# app/services/agents/response_structurer.py

import json
from datetime import datetime
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)

class ResponseStructurer:
    async def structure_response(
        self,
        parent_metadata: Dict[str, Any],
        original_prompt: str,
        conversation_history: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Structures the final response into a consistent JSON format.
        
        Args:
            parent_metadata (dict): The final result dictionary from ParentAgent's processing.
                                    Example keys: has_artifact, summary, component_type, sub_type, data, style, configuration, metadata, content
            original_prompt (str): The original user query.
            conversation_history (List[dict]): The conversation messages leading to this response.
        
        Returns:
            Dict[str, Any]: A structured JSON response with a stable schema.
        """

        # Extract fields from the parent result, using defaults if missing
        has_artifact = parent_metadata.get("has_artifact", False)
        summary = parent_metadata.get("summary", "")
        component_type = parent_metadata.get("component_type", None)
        sub_type = parent_metadata.get("sub_type", None)
        data = parent_metadata.get("data", None)
        style = parent_metadata.get("style", {})
        configuration = parent_metadata.get("configuration", {})
        metadata = parent_metadata.get("metadata", {})
        
        # 'content' might come from either a quick text response or artifact summary
        content = parent_metadata.get("content")
        if not content and not has_artifact:
            # If no artifact, content should be textual response from the quick responder
            content = parent_metadata.get("content", "No content available.")
        elif not content and has_artifact:
            # If artifact exists but no 'content', use summary
            content = summary or "Here's your requested artifact visualization."

        # Construct a stable schema with all fields present
        structured_response = {
            "agent": "ParentAgent",
            "original_prompt": original_prompt,
            "timestamp": datetime.utcnow().isoformat(),
            "conversation_context_length": len(conversation_history),
            "has_artifact": has_artifact,
            "component_type": component_type,
            "sub_type": sub_type,
            "data": data,
            "style": style,
            "configuration": configuration,
            "metadata": metadata,
            "summary": summary,
            "content": content
        }

        # This structured_response can now be returned or logged as needed
        logger.info(f"Structured response generated: {json.dumps(structured_response, indent=2)}")

        return structured_response

# Example usage (in your router or after parent agent completes):
# response_structurer = ResponseStructurer()
# final_structured = await response_structurer.structure_response(
#     parent_metadata=parent_agent_final,
#     original_prompt=user_prompt,
#     conversation_history=conversation_history
# )
#
# # final_structured is a stable JSON that can be returned to the client or further processed.
