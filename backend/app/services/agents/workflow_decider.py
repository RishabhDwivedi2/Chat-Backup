# app/services/agents/workflow_decider.py

from typing import Dict, Any
import logging
from app.services.gpt_service import GPTService
import json
from app.utils.json_handler import JSONHandler

logger = logging.getLogger(__name__)

class WorkflowDecider:
    """
    Agent responsible for deciding the workflow and determining if artifact creation is needed,
    without handling the actual artifact creation.
    """
    
    def __init__(self, gpt_service: GPTService):
        self.gpt_service = gpt_service

    async def decide_workflow(
        self,
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Analyze metadata to determine workflow and artifact requirements.
        """
        decision_prompt = f"""
        Analyze the following metadata to determine if the request requires an artifact response.
        
        METADATA: {metadata}

        CONSIDER THE FOLLOWING CRITERIA:

        1. Data Presentation Needs:
           - Does the query ask for statistics, numbers, or metrics?
           - Is there a need to compare multiple data points?
           - Would the information benefit from structured presentation?
           - Are there multiple categories or dimensions of data?

        2. Query Characteristics:
           - Is it asking for trends or patterns?
           - Does it involve time-based comparisons?
           - Are there multiple metrics to be shown together?
           - Would a visual or structured format improve understanding?

        3. Response Complexity:
           - Would plain text be insufficient to present the information clearly?
           - Are there relationships between different data points?
           - Does the data have a natural hierarchical or tabular structure?

        Respond in JSON format:
        {{
            "selected_agent": "ParentAgent or ParentAgent",
            "requires_artifact": true/false,
            "reasoning": "Clear explanation of why artifact is needed or not needed based on query characteristics"
        }}
        """

        gpt_response = await self.gpt_service.get_chat_response(
            prompt=decision_prompt,
            max_tokens=200,
            temperature=0.1
        )

        try:
            decision_data = JSONHandler.extract_clean_json(gpt_response)
            requires_artifact = decision_data.get("requires_artifact", False)
            selected_agent = decision_data.get("selected_agent", "ParentAgent")
            reasoning = decision_data.get("reasoning", "No reasoning provided")
        except Exception as e:
            logger.error(f"Error parsing decision data: {e}")
            # Analyze the query text directly for fallback decision
            query_indicators = ["statistics", "compare", "trends", "metrics", "performance", "data", "table", "chart"]
            requires_artifact = any(indicator in metadata.get("analysis", "").lower() for indicator in query_indicators)
            selected_agent = "ParentAgent" if requires_artifact else "ParentAgent"
            reasoning = "Fallback analysis based on query keywords and content type"

        decision_metadata = {
            "selected_agent": selected_agent,
            "analysis": metadata.get("analysis", "No analysis available"),
            "reasoning": reasoning,
            "artifact_creation": requires_artifact
        }

        logger.info(f"Workflow decision made: {json.dumps(decision_metadata, indent=2)}")
        return decision_metadata