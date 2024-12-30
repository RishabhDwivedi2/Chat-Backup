# app/services/agents/parent_agent.py

import logging
from typing import Dict, Any, Optional
from app.services.gpt_service import GPTService
from app.utils.json_handler import JSONHandler
import json

logger = logging.getLogger(__name__)

class ParentAgent:
    ALLOWED_COMPONENTS = {"table", "chart", "card", "text"}
    ALLOWED_CHART_SUBTYPES = {"bar", "line", "pie", "radial", "radar","area"}

    def __init__(self, gpt_service: GPTService):
        self.gpt_service = gpt_service
        self.query_analyzer = QueryAnalyzer(gpt_service=gpt_service)
        self.quick_responder = QuickResponder(gpt_service=gpt_service)
        self.artifact_analyzer = ArtifactAnalyzer(
            gpt_service=gpt_service,
            allowed_components=self.ALLOWED_COMPONENTS,
            allowed_chart_subtypes=self.ALLOWED_CHART_SUBTYPES
        )
        self.artifact_constructor = ArtifactConstructor(gpt_service=gpt_service)
        self.response_gatherer = ResponseGatherer()

    async def process(self, prompt: str, metadata: Dict[str, Any], conversation_history: Dict[str, Any]) -> Dict[str, Any]:
        logger.info("=== Parent Agent Started ===")
        analysis = metadata.get("analysis", "")
        reasoning = metadata.get("reasoning", "")
        artifact_needed_from_decider = metadata.get("artifact_creation", False)

        # Step 1: Query Analysis
        query_analysis_result = await self.query_analyzer.analyze(
            prompt=prompt,
            analysis=analysis,
            reasoning=reasoning,
            artifact_needed_from_decider=artifact_needed_from_decider
        )

        if query_analysis_result["requires_artifact"]:
            # Artifact path
            artifact_analysis_result = await self.artifact_analyzer.determine_component(query_analysis_result["analysis"])
            
            if not artifact_analysis_result.get("success", False):
                # Fallback to quick response if artifact analysis fails
                final_response = await self._handle_quick_response(prompt, query_analysis_result["analysis"], conversation_history)
                logger.info("=== Parent Agent Final Response ===")
                logger.info(final_response)
                return final_response
            
            artifact_result = await self.artifact_constructor.construct_artifact(
                prompt=prompt,
                component_type=artifact_analysis_result["component_type"],
                component_subtype=artifact_analysis_result["component_subtype"],
                analysis=artifact_analysis_result["analysis"]
            )
            
            if not artifact_result.get("success", False):
                # Fallback to quick response if artifact construction fails
                final_response = await self._handle_quick_response(prompt, query_analysis_result["analysis"], conversation_history)
                logger.info("=== Parent Agent Final Response ===")
                logger.info(final_response)
                return final_response
            
            final_response = await self.response_gatherer.gather(artifact_response=artifact_result)
            logger.info("=== Parent Agent Final Response ===")
            logger.info(final_response)
            return final_response
        else:
            # Quick response path
            final_response = await self._handle_quick_response(prompt, query_analysis_result["analysis"], conversation_history)
            logger.info("=== Parent Agent Final Response ===")
            logger.info(final_response)
            return final_response

    async def _handle_quick_response(self, prompt: str, analysis: str, conversation_history: Dict[str, Any]) -> Dict[str, Any]:
        quick_response_result = await self.quick_responder.respond(
            prompt=prompt,
            analysis=analysis,
            conversation_history=conversation_history
        )
        return await self.response_gatherer.gather(quick_response=quick_response_result)


class QueryAnalyzer:
    def __init__(self, gpt_service: GPTService):
        self.gpt_service = gpt_service

    async def analyze(self, prompt: str, analysis: str, reasoning: str, artifact_needed_from_decider: bool) -> Dict[str, Any]:
        analysis_prompt = f"""
        You are a Query Analysis Agent responsible for determining if a response requires visualization or structured data presentation.
        
        Original Query: {prompt}
        Initial Analysis: {analysis}
        Initial Reasoning: {reasoning}
        Workflow Suggestion for Artifact: {artifact_needed_from_decider}

        Analyze the complexity and nature of the required response.
        Consider:
        1. Does the query involve data comparison, trends, or patterns?
        2. Would a visual representation enhance understanding?
        3. Is the data structured enough for visualization?
        4. Is the response better served with plain text?

        Return a JSON with your analysis:
        {{
            "requires_artifact": boolean,
            "analysis": "detailed analysis of requirements",
            "data_points": ["list of key data points needed"],
            "visualization_benefit": "explanation of why visualization would/wouldn't help",
            "complexity_level": "high/medium/low"
        }}
        """

        response = await self.gpt_service.get_chat_response(
            prompt=analysis_prompt,
            max_tokens=400,
            temperature=0.2
        )
        
        analysis_result = JSONHandler.extract_clean_json(response)
        
        return {
            "requires_artifact": analysis_result.get("requires_artifact", artifact_needed_from_decider),
            "analysis": analysis_result.get("analysis", analysis),
            "data_points": analysis_result.get("data_points", []),
            "complexity_level": analysis_result.get("complexity_level", "medium")
        }


class QuickResponder:
    def __init__(self, gpt_service: GPTService):
        self.gpt_service = gpt_service

    async def respond(self, prompt: str, analysis: str, conversation_history: Dict[str, Any]) -> Dict[str, Any]:
        response_prompt = f"""
        Generate a clear and concise response to the user's query.
        
        Original Query: {prompt}
        Analysis: {analysis}

        Requirements:
        1. Provide a direct and helpful answer
        2. Include relevant context if necessary
        3. Use natural, conversational language
        4. Keep the response focused and to the point

        Return only the response text that should be shown to the user.
        """

        response = await self.gpt_service.get_chat_response(
            prompt=response_prompt,
            conversation_history=conversation_history,
            max_tokens=300,
            temperature=0.7
        )

        return {
            "content": response,
            "has_artifact": False
        }


class ArtifactAnalyzer:
    def __init__(self, gpt_service: GPTService, allowed_components: set, allowed_chart_subtypes: set):
        self.gpt_service = gpt_service
        self.allowed_components = allowed_components
        self.allowed_chart_subtypes = allowed_chart_subtypes

    async def determine_component(self, analysis: str) -> Dict[str, Any]:
        """
        Determine component_type and component_subtype strictly via GPT response.
        If the analysis explicitly suggests a certain artifact or subtype, GPT should strongly adhere to it.
        Otherwise, GPT chooses the best fit.

        Steps:
        1. Ask GPT for component_type and component_subtype.
        2. If chart chosen but subtype missing/invalid, ask GPT to correct it.
        3. Return the chosen component_type, component_subtype, and the original analysis.
        """

        component_prompt = f"""
        You are an Artifact Analyzer Agent. You have the following information from the Query Analyzer:

        Analysis: {analysis}

        The analysis may or may not explicitly mention which artifact or subtype to use.
        If the analysis explicitly suggests a certain component type or chart subtype, adhere to that suggestion.

        If not explicitly stated, choose from:
        Allowed components: {sorted(self.allowed_components)}
        Allowed chart subtypes (if chart chosen): {sorted(self.allowed_chart_subtypes)}

        Consider the data's nature, complexity, and visualization needs.
        
        Return ONLY JSON:
        {{
          "component_type": "<one from allowed components>",
          "component_subtype": "<one from allowed chart subtypes if chart, else null>",
          "reasoning": "Brief explanation"
        }}
        """

        first_response = await self.gpt_service.get_chat_response(
            prompt=component_prompt,
            max_tokens=300,
            temperature=0.3
        )

        decision = JSONHandler.extract_clean_json(first_response)
        component_type = decision.get("component_type")
        component_subtype = decision.get("component_subtype")

        # If chart chosen but subtype is missing or invalid, ask GPT to fix it.
        if component_type == "chart" and (not component_subtype or component_subtype not in self.allowed_chart_subtypes):
            fix_prompt = f"""
            The chosen component_type is "chart" but the subtype provided is missing or invalid.
            Allowed chart subtypes: {sorted(self.allowed_chart_subtypes)}

            Based on previous analysis:
            {analysis}

            Please provide a corrected JSON with a valid chart subtype, keeping component_type as chart.

            Return ONLY JSON:
            {{
              "component_type": "chart",
              "component_subtype": "<valid subtype from allowed list>",
              "reasoning": "Updated reasoning"
            }}
            """

            fix_response = await self.gpt_service.get_chat_response(
                prompt=fix_prompt,
                max_tokens=100,
                temperature=0.2
            )
            fixed_decision = JSONHandler.extract_clean_json(fix_response)
            component_type = fixed_decision.get("component_type", component_type)
            component_subtype = fixed_decision.get("component_subtype", component_subtype)
            reasoning = fixed_decision.get("reasoning", decision.get("reasoning", "No reasoning provided"))
        else:
            reasoning = decision.get("reasoning", "No reasoning provided")

        return {
            "success": True,
            "component_type": component_type,
            "component_subtype": component_subtype if component_type == "chart" else None,
            "analysis": analysis,  # Include the original analysis for the calling code.
            "reasoning": reasoning
        }

class ArtifactConstructor:
    def __init__(self, gpt_service: GPTService):
        self.gpt_service = gpt_service

    async def construct_artifact(self, prompt: str, component_type: str, component_subtype: str, analysis: str) -> Dict[str, Any]:
        artifact_json = await self._attempt_construction(prompt, component_type, component_subtype, analysis)
        
        # If artifact_json is empty or invalid, or missing subtype for chart, attempt a fallback request
        if not artifact_json or not isinstance(artifact_json, dict):
            logger.warning("Initial artifact JSON extraction failed. Attempting fallback request for cleaner JSON.")
            artifact_json = await self._fallback_json_request(prompt, component_type, component_subtype, analysis)
        
        # If it's a chart, ensure subtype is present. If not, re-ask for a corrected JSON.
        if component_type == "chart" and (not artifact_json.get("component_subtype") or artifact_json.get("component_subtype") not in ParentAgent.ALLOWED_CHART_SUBTYPES):
            logger.warning("Chart artifact missing or invalid 'component_subtype'. Re-requesting a corrected JSON.")
            artifact_json = await self._fallback_json_request(prompt, component_type, component_subtype, analysis, force_subtype=component_subtype)

        if not artifact_json:
            return {"success": False, "error": "Failed to produce a valid artifact JSON after fallback."}

        return {
            "success": True,
            "content": "Here's a structured representation of the data.",
            "artifact_json": artifact_json,
            "has_artifact": True
        }

    async def _attempt_construction(self, prompt: str, component_type: str, component_subtype: str, analysis: str) -> Optional[dict]:
        component_metadata = await self._get_component_metadata(component_type, component_subtype)

        construction_prompt = f"""
        Create a detailed artifact definition based on the following:
        
        Original Query: {prompt}
        Analysis: {analysis}
        Component Type: {component_type}
        Component Subtype: {component_subtype if component_subtype else 'N/A'}

        Required Structure (JSON):
        {component_metadata.get("structure", {})}

        The data should align with the query context.
        Return ONLY a JSON object.
        """

        artifact_json_str = await self.gpt_service.get_chat_response(
            prompt=construction_prompt,
            max_tokens=800,
            temperature=0.5
        )
        
        artifact_json = JSONHandler.extract_clean_json(artifact_json_str)
        if artifact_json and self._validate_artifact_structure(artifact_json, component_metadata["structure"]):
            return artifact_json
        return None

    async def _fallback_json_request(self, prompt: str, component_type: str, component_subtype: str, analysis: str, force_subtype: Optional[str] = None) -> Optional[dict]:
        component_metadata = await self._get_component_metadata(component_type, force_subtype or component_subtype)

        fallback_prompt = f"""
        The previously generated JSON was incomplete or invalid.
        Please regenerate a simpler, valid JSON artifact with the same constraints.

        Original Query: {prompt}
        Analysis: {analysis}
        Component Type: {component_type}
        Component Subtype: {force_subtype or component_subtype or 'N/A'}

        Required Structure (JSON):
        {component_metadata.get("structure", {})}

        Provide a minimal, valid example. Return ONLY the JSON object.
        """

        artifact_json_str = await self.gpt_service.get_chat_response(
            prompt=fallback_prompt,
            max_tokens=500,
            temperature=0.5
        )
        artifact_json = JSONHandler.extract_clean_json(artifact_json_str)
        if artifact_json and self._validate_artifact_structure(artifact_json, component_metadata["structure"]):
            return artifact_json
        return None

    async def _get_component_metadata(self, component_type: str, component_subtype: str = None) -> Dict[str, Any]:
        base_structure = {
            "title": "string",
            "description": "string",
            "component_type": component_type,
            "style": {
                "width": "string",
                "height": "string"
            }
        }

        if component_type == "chart":
            return {
                "structure": {
                    **base_structure,
                    "component_subtype": component_subtype,
                    "data": {
                        "labels": ["array of label strings"],
                        "values": [
                            {
                                "entity": "string",
                                "data": ["array of numeric values"]
                            }
                        ]
                    },
                    "configuration": {
                        "axes": {
                            "x": {"title": "string"},
                            "y": {"title": "string"}
                        },
                        "legend": "boolean"
                    }
                }
            }
        elif component_type == "table":
            return {
                "structure": {
                    **base_structure,
                    "data": {
                        "headers": ["array of column names"],
                        "rows": ["array of data rows"]
                    }
                }
            }
        
        # Default structure if not defined otherwise
        return {"structure": base_structure}

    def _validate_artifact_structure(self, artifact: Dict[str, Any], required_structure: Dict[str, Any]) -> bool:
        """Validates that the artifact follows the required structure"""
        def validate_dict(actual: Dict[str, Any], expected: Dict[str, Any]) -> bool:
            for key, value in expected.items():
                if key not in actual:
                    return False
                if isinstance(value, dict) and isinstance(actual[key], dict):
                    if not validate_dict(actual[key], value):
                        return False
                # If expected is not a dict, we just check existence.
            return True

        return validate_dict(artifact, required_structure)


class ResponseGatherer:
    async def gather(self, quick_response: Dict[str, Any] = None, artifact_response: Dict[str, Any] = None) -> Dict[str, Any]:
        """Gathers and formats the final response in a readable way for logs."""
        if artifact_response and artifact_response.get("has_artifact"):
            artifact_json = artifact_response.get("artifact_json", {})
            
            component_type = artifact_json.get("component_type")
            component_subtype = artifact_json.get("component_subtype") if component_type == "chart" else None

            final_result = {
                "has_artifact": True,
                "summary": artifact_response.get("content", "Here's the visualization you requested."),
                "component_type": component_type,
                "sub_type": component_subtype,
                "data": artifact_json.get("data"),
                "style": artifact_json.get("style", {}),
                "configuration": artifact_json.get("configuration", {}),
                "metadata": {
                    "title": artifact_json.get("title"),
                    "description": artifact_json.get("description")
                }
            }
        else:
            final_result = {
                "has_artifact": False,
                "content": quick_response.get("content") if quick_response else "No content available.",
                "metadata": {}
            }

        # Using json.dumps with indent=2 provides a neat, multiline JSON format:
        # Arrays and objects are properly spaced and newlined, producing a result
        # similar to the example you provided.
        formatted_response = json.dumps(final_result, indent=2)
        logger.info("\n=== FINAL STRUCTURED RESPONSE ===\n" + formatted_response + "\n===============================\n")

        return final_result