from typing import Dict, Any, Optional, List
import json
import logging
from datetime import datetime
from app.services.gpt_service import GPTService

logger = logging.getLogger(__name__)

class ResponseStructurer:
    """
    Agent responsible for structuring response metadata into a consistent format
    that's easily consumable by the frontend.
    """
    
    def __init__(self, gpt_service: GPTService):
        self.gpt_service = gpt_service
        
    async def structure_response(
        self,
        parent_metadata: Dict[str, Any],
        original_prompt: str,
        conversation_history: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        try:
            has_artifact = parent_metadata.get("has_artifact", False)
            content = parent_metadata.get("content")
            summary = parent_metadata.get("summary")
            component_type = parent_metadata.get("component_type") if has_artifact else None
            artifact_data = parent_metadata.get("data", {})

            # Generate content if none exists and we have an artifact
            if not content and has_artifact:
                content_prompt = f"""
                Generate a brief introductory message for showing visualization of data.
                Context: User asked about {original_prompt}
                Component: {component_type}
                Make it sound natural and helpful (1-2 sentences).
                """
                
                content = await self.gpt_service.get_chat_response(
                    prompt=content_prompt,
                    max_tokens=100,
                    temperature=0.7
                )

            # Build the standardized response structure
            structured_response = {
                "content": content.strip() if content else "Let me help you visualize this data.",
                "has_artifact": has_artifact,
                "component_type": component_type,
                "sub_type": artifact_data.get("type") if component_type == "Chart" else None,
                "data": {
                    "labels": artifact_data.get("labels", []),
                    "values": self._extract_values(artifact_data),
                    "style": artifact_data.get("style", {
                        "width": "800px",
                        "height": "500px"
                    })
                } if has_artifact else None,
                "summary": summary if has_artifact else None,
                "metadata": {
                    "timestamp": datetime.utcnow().isoformat(),
                    "query": original_prompt,
                    "processing_info": {
                        "version": "2.0",
                        "generated_at": datetime.utcnow().isoformat(),
                        "context_length": len(conversation_history) if conversation_history else 0
                    }
                }
            }

            # Add component-specific data processing
            if has_artifact:
                structured_response = self._process_component_specific_data(
                    structured_response,
                    component_type,
                    artifact_data
                )

            logger.info(f"Structured response generated: {json.dumps(structured_response, indent=2)}")
            return structured_response

        except Exception as e:
            logger.error(f"Error in response structuring: {str(e)}", exc_info=True)
            return self._generate_fallback_response(original_prompt)

    def _extract_values(self, artifact_data: Dict[str, Any]) -> List[Any]:
        """Extract values from artifact data regardless of structure."""
        if "data" in artifact_data and "values" in artifact_data["data"]:
            return artifact_data["data"]["values"]
        elif "values" in artifact_data:
            return artifact_data["values"]
        elif "rows" in artifact_data:  # For table data
            return artifact_data["rows"]
        return []

    def _process_component_specific_data(
        self,
        response: Dict[str, Any],
        component_type: str,
        artifact_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Add component-specific data processing based on component type."""
        
        if component_type == "Table":
            response["data"].update({
                "headers": artifact_data.get("headers", []),
                "rows": artifact_data.get("rows", []),
                "title": artifact_data.get("title", "Data Table")
            })
            
        elif component_type == "Chart":
            response["data"].update({
                "title": artifact_data.get("title", "Chart"),
                "axis_labels": {
                    "x": artifact_data.get("x_axis_label", ""),
                    "y": artifact_data.get("y_axis_label", "")
                },
                "config": {
                    "show_grid": True,
                    "show_legend": True,
                    "interactive": True
                }
            })
            
        elif component_type == "Card":
            response["data"].update({
                "title": artifact_data.get("title", "Metric Card"),
                "metrics": artifact_data.get("metrics", []),
                "footer": artifact_data.get("footer", "")
            })

        return response

    def _generate_fallback_response(self, original_prompt: str) -> Dict[str, Any]:
        """Generate a standardized fallback response."""
        return {
            "content": "Unable to generate structured response",
            "has_artifact": False,
            "component_type": None,
            "sub_type": None,
            "data": None,
            "summary": None,
            "metadata": {
                "timestamp": datetime.utcnow().isoformat(),
                "query": original_prompt,
                "processing_info": {
                    "version": "2.0",
                    "generated_at": datetime.utcnow().isoformat(),
                    "context_length": 0,
                    "status": "fallback"
                }
            }
        }