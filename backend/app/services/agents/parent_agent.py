# app/services/agents/parent_agent.py

from typing import Dict, Any, Optional, List
import json
import logging
from app.services.gpt_service import GPTService

logger = logging.getLogger(__name__)

class QuickResponder:
    """Sub-agent responsible for generating quick responses for simple queries."""
    
    async def respond(
        self, 
        prompt: str, 
        gpt_service: GPTService,
        conversation_history: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        # Format conversation history for context
        context = ""
        if conversation_history:
            recent_messages = conversation_history[-5:]  # Get last 5 messages
            context = "\n".join([
                f"{msg.get('role', 'unknown')}: {msg.get('content', '')}"
                for msg in recent_messages
            ])
            
        quick_response_prompt = f"""
        Consider the following conversation context and respond to the prompt:
        
        CONVERSATION CONTEXT:
        {context if context else "No prior conversation"}
        
        CURRENT PROMPT: "{prompt}"
        
        Provide a contextually appropriate response that maintains the conversation flow.
        """
        
        gpt_response = await gpt_service.get_chat_response(
            prompt=quick_response_prompt,
            max_tokens=150,
            temperature=0.5
        )

        return {
            "content": gpt_response.strip(),
            "has_artifact": False,
            "data": None,
            "component_type": None,
            "summary": None
        }

class ArtifactConstructor:
    """Sub-agent responsible for constructing artifacts with dynamic, relevant data and styles."""
    
    async def construct_artifact(
        self,
        component_type: str,
        chart_type: str,
        prompt: str,
        gpt_service: GPTService,
        conversation_history: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Construct an artifact with context awareness.
        
        Args:
            component_type (str): Type of component to create
            chart_type (str): Type of chart if component is a chart
            prompt (str): Current user query
            gpt_service (GPTService): GPT service instance
            conversation_history (Optional[List[Dict[str, Any]]]): Previous conversation messages
        """
        try:
            # Format conversation context
            context_summary = self._format_conversation_history(conversation_history)
            
            # Detailed prompt to generate data and metadata dynamically
            artifact_prompt = f"""
            Generate metadata for a {chart_type} {component_type} considering the following context:

            QUERY: "{prompt}"
            CONVERSATION CONTEXT:
            {context_summary}
            
            Generate complete and contextually relevant JSON metadata for the {chart_type} {component_type}, including:
            1. Title: A descriptive title that reflects both the query and conversation context
            2. Style: Specific width and height settings
            3. Labels: Context-appropriate labels
            4. Data: Relevant numeric values
            5. Additional metadata that might be useful
            
            Note: Use simulated/demo data that makes sense in the conversation context.

            Respond in JSON format:
            {{
                "title": "Clear, context-aware title",
                "style": {{"width": "800px", "height": "500px"}},
                "labels": ["Label1", "Label2", "Label3", ...],
                "data": {{
                    "values": [numeric values],
                    "metadata": {{
                        "description": "Context-aware description",
                        "insights": ["Key insight 1", "Key insight 2"],
                        "source": "Simulated data for demonstration"
                    }}
                }}
            }}
            """

            # Get GPT's response
            gpt_response = await gpt_service.get_chat_response(
                prompt=artifact_prompt,
                max_tokens=500,
                temperature=0.4
            )

            # Parse GPT's response for artifact metadata
            try:
                artifact_data = json.loads(gpt_response)
            except json.JSONDecodeError:
                logger.error("Failed to parse GPT response for artifact as JSON")
                return self._generate_fallback_artifact(component_type, chart_type)

            return {
                "has_artifact": True,
                "component_type": component_type,
                "data": {
                    "type": chart_type,
                    "title": artifact_data.get("title", "Generated Chart"),
                    "style": artifact_data.get("style", {"width": "800px", "height": "500px"}),
                    "labels": artifact_data.get("labels", ["Label1", "Label2", "Label3"]),
                    "data": artifact_data.get("data", {
                        "values": [25, 50, 25],
                        "metadata": {
                            "description": "Fallback description",
                            "insights": ["No specific insights available"],
                            "source": "Simulated data"
                        }
                    })
                }
            }

        except Exception as e:
            logger.error(f"Error constructing artifact: {str(e)}")
            return self._generate_fallback_artifact(component_type, chart_type)

    def _format_conversation_history(
        self,
        conversation_history: Optional[List[Dict[str, Any]]]
    ) -> str:
        """Format conversation history for use in prompts."""
        if not conversation_history:
            return "No prior conversation"
            
        formatted_history = []
        # Take last 5 messages for recent context
        for msg in conversation_history[-5:]:
            role = msg.get("role", "unknown")
            content = msg.get("content", "")
            formatted_history.append(f"{role}: {content}")
            
        return "\n".join(formatted_history)

    def _generate_fallback_artifact(
        self,
        component_type: str,
        chart_type: str
    ) -> Dict[str, Any]:
        """Generate a fallback artifact when construction fails."""
        return {
            "has_artifact": True,
            "component_type": component_type,
            "data": {
                "type": chart_type,
                "title": f"Generated {chart_type} {component_type}",
                "style": {"width": "800px", "height": "500px"},
                "labels": ["Category A", "Category B", "Category C"],
                "data": {
                    "values": [33, 33, 34],
                    "metadata": {
                        "description": "Fallback visualization",
                        "insights": ["Data unavailable", "Using placeholder values"],
                        "source": "Simulated data (fallback)"
                    }
                }
            }
        }

    async def construct_specific_chart(
        self,
        chart_type: str,
        prompt: str,
        gpt_service: GPTService,
        conversation_history: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """Construct a specific type of chart with context awareness."""
        context_summary = self._format_conversation_history(conversation_history)
        
        chart_prompt = f"""
        Generate specific data for a {chart_type} chart based on:

        QUERY: "{prompt}"
        CONVERSATION CONTEXT:
        {context_summary}
        
        Provide chart data in JSON format specific to {chart_type} charts.
        Include:
        - Appropriate data structure for {chart_type} visualization
        - Context-aware labels and values
        - Relevant metadata and descriptions
        """
        
        try:
            response = await gpt_service.get_chat_response(
                prompt=chart_prompt,
                max_tokens=400,
                temperature=0.3
            )
            
            chart_data = json.loads(response)
            return {
                "has_artifact": True,
                "component_type": "Chart",
                "data": {
                    "type": chart_type,
                    **chart_data
                }
            }
        except Exception as e:
            logger.error(f"Error constructing {chart_type} chart: {str(e)}")
            return self._generate_fallback_artifact("Chart", chart_type)


class ArtifactSummaryProvider:
    """Sub-agent responsible for providing detailed summary for artifacts."""
    
    def __init__(self, gpt_service: GPTService):
        self.gpt_service = gpt_service

    async def provide_summary(
        self,
        component_type: str,
        chart_type: str,
        artifact_data: Dict[str, Any],
        conversation_history: Optional[List[Dict[str, Any]]] = None
    ) -> str:
        context_summary = ""
        if conversation_history:
            recent_messages = conversation_history[-5:]
            context_summary = "\n".join([
                f"{msg.get('role', 'unknown')}: {msg.get('content', '')}"
                for msg in recent_messages
            ])

        summary_prompt = f"""
        Consider the following conversation context and artifact data:
        
        CONVERSATION CONTEXT:
        {context_summary if context_summary else "No prior conversation"}
        
        ARTIFACT TYPE: {component_type} ({chart_type if chart_type else 'N/A'})
        ARTIFACT DATA: {json.dumps(artifact_data, indent=2)}
        
        Generate a comprehensive summary that:
        1. Relates the artifact to the conversation context
        2. Explains the main insights or findings
        3. Connects the data to any relevant prior messages
        4. Notes that the data is simulated for demonstration
        
        Provide a concise and contextual summary paragraph.
        """

        summary = await self.gpt_service.get_chat_response(
            prompt=summary_prompt,
            max_tokens=200,
            temperature=0.5
        )

        return summary.strip()


class ParentAgent:
    """Parent agent that generates responses based on WorkflowDecider's metadata."""
    
    def __init__(self, gpt_service: GPTService):
        self.gpt_service = gpt_service
        self.quick_responder = QuickResponder()
        self.artifact_constructor = ArtifactConstructor()
        self.artifact_summary_provider = ArtifactSummaryProvider(gpt_service=gpt_service)

    async def process(
        self, 
        prompt: str, 
        metadata: Dict[str, Any],
        conversation_history: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        requires_artifact = metadata.get("artifact_creation", False)
        analysis = metadata.get("analysis", "")
        reasoning = metadata.get("reasoning", "")

        # If no artifact is needed, use QuickResponder with context
        if not requires_artifact:
            quick_response_metadata = await self.quick_responder.respond(
                prompt, 
                self.gpt_service, 
                conversation_history
            )
            return quick_response_metadata

        # Get introductory content first
        intro_prompt = f"""
        Create a natural introductory response for the following request:
        
        USER QUERY: {prompt}
        ANALYSIS: {analysis}
        CONTEXT: {self._format_conversation_history(conversation_history) if conversation_history else "No prior context"}
        
        Write a brief, engaging response that:
        1. Acknowledges the user's request
        2. Mentions you'll create a visualization or structured view
        3. Sounds natural and helpful
        
        Examples:
        - "I'll create a chart to help you visualize these trends clearly."
        - "Let me break down this data in a table for better understanding."
        - "I'll organize this information into a structured visualization for you."
        
        Keep it brief (1-2 sentences) and conversational.
        """

        intro_content = await self.gpt_service.get_chat_response(
            prompt=intro_prompt,
            max_tokens=100,
            temperature=0.7
        )

        # Get component decision
        component_decision_prompt = f"""
        Based on the following analysis and context, determine the most appropriate visualization format:

        ANALYSIS: {analysis}
        REASONING: {reasoning}
        QUERY: {prompt}
        CONVERSATION CONTEXT: {self._format_conversation_history(conversation_history) if conversation_history else "No prior context"}

        Select the most appropriate format:
        1. For statistical comparisons and multi-dimensional data: use "Table"
        2. For trends and time-series data: use "Chart" with "line" type
        3. For part-to-whole relationships: use "Chart" with "pie" type
        4. For category comparisons: use "Chart" with "bar" type
        5. For multi-metric comparisons: use "Chart" with "radar" type
        6. For cumulative data: use "Chart" with "area" type
        7. For metric summaries: use "Card"

        Respond in JSON format:
        {{
            "component_type": "Chart" or "Table" or "Card",
            "chart_type": "line" or "pie" or "bar" or "radar" or "area" (only if component_type is "Chart"),
            "reasoning": "Brief explanation of why this format was chosen"
        }}
        """

        response = await self.gpt_service.get_chat_response(
            prompt=component_decision_prompt,
            max_tokens=200,
            temperature=0.3
        )

        try:
            component_decision = json.loads(response)
            component_type = component_decision.get("component_type", "Table")
            chart_type = component_decision.get("chart_type") if component_type == "Chart" else None
        except json.JSONDecodeError:
            logger.error("Failed to parse component decision")
            component_type = "Table"
            chart_type = None

        # Construct the appropriate artifact
        if component_type == "Chart" and chart_type:
            artifact_response = await self.artifact_constructor.construct_artifact(
                component_type=component_type,
                chart_type=chart_type,
                prompt=prompt,
                gpt_service=self.gpt_service,
                conversation_history=conversation_history
            )
        elif component_type == "Table":
            artifact_response = await self.construct_table_artifact(
                prompt=prompt,
                analysis=analysis,
                conversation_history=conversation_history
            )
        elif component_type == "Card":
            artifact_response = await self.construct_card_artifact(
                prompt=prompt,
                analysis=analysis,
                conversation_history=conversation_history
            )
        else:
            logger.error(f"Unsupported component type: {component_type}")
            return await self.quick_responder.respond(
                prompt, 
                self.gpt_service,
                conversation_history
            )
        
        artifact_response["content"] = intro_content.strip()

        # Generate summary with context
        if artifact_response.get("has_artifact", False):
            summary = await self.artifact_summary_provider.provide_summary(
                component_type=component_type,
                chart_type=artifact_response["data"].get("type"),
                artifact_data=artifact_response["data"],
                conversation_history=conversation_history
            )
            artifact_response["summary"] = summary

        logger.info(f"Parent Agent generated artifact response based on workflow metadata: {json.dumps(artifact_response, indent=2)}")
        return artifact_response

    def _format_conversation_history(self, conversation_history: Optional[List[Dict[str, Any]]]) -> str:
        """Format conversation history for prompt inclusion."""
        if not conversation_history:
            return "No prior conversation"
            
        formatted_history = []
        for msg in conversation_history[-5:]:  # Include last 5 messages for context
            role = msg.get("role", "unknown")
            content = msg.get("content", "")
            formatted_history.append(f"{role}: {content}")
            
        return "\n".join(formatted_history)

    async def construct_table_artifact(
        self,
        prompt: str,
        analysis: str,
        conversation_history: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """Construct a table artifact with context consideration."""
        context_summary = self._format_conversation_history(conversation_history)
        
        table_prompt = f"""
        Generate a structured table dataset for the following query and context:
        
        QUERY: "{prompt}"
        ANALYSIS: "{analysis}"
        CONVERSATION CONTEXT: {context_summary}
        
        Provide complete table data in JSON format:
        {{
            "title": "Table title",
            "headers": ["Column1", "Column2", ...],
            "rows": [
                {{"Column1": "value", "Column2": "value", ...}},
                ...
            ]
        }}
        """
        
        response = await self.gpt_service.get_chat_response(
            prompt=table_prompt,
            max_tokens=800,
            temperature=0.3
        )

        try:
            response = response.replace("```json", "").replace("```", "").strip()
            table_data = json.loads(response)
            
            return {
                "has_artifact": True,
                "component_type": "Table",
                "data": {
                    "type": "table",
                    "title": table_data.get("title", "Data Table"),
                    "headers": table_data.get("headers", []),
                    "rows": table_data.get("rows", []),
                    "labels": table_data.get("headers", []),
                    "data": {
                        "values": table_data.get("rows", [])
                    }
                }
            }
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse table data: {e}")
            return self.generate_fallback_table()

    def generate_fallback_table(self) -> Dict[str, Any]:
        """Generate a fallback table structure."""
        fallback_data = {
            "has_artifact": True,
            "component_type": "Table",
            "data": {
                "type": "table",
                "title": "Data Summary",
                "headers": ["Category", "Value"],
                "rows": [{"Category": "No Data", "Value": "N/A"}],
                # Add these fields to maintain compatibility with summary provider
                "labels": ["Category", "Value"],
                "data": {
                    "values": [{"Category": "No Data", "Value": "N/A"}]
                }
            }
        }
        return fallback_data

    async def construct_card_artifact(
        self,
        prompt: str,
        analysis: str,
        conversation_history: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Construct a card artifact for metric summaries with context consideration.
        
        Args:
            prompt (str): The current user query
            analysis (str): Analysis from workflow decider
            conversation_history (Optional[List[Dict[str, Any]]]): Previous conversation messages
        """
        try:
            # Format conversation context
            context_summary = self._format_conversation_history(conversation_history)
            
            card_prompt = f"""
            Generate a metric card dataset based on the following query and context:
            
            QUERY: "{prompt}"
            ANALYSIS: "{analysis}"
            CONVERSATION CONTEXT: {context_summary}
            
            Create a card that summarizes key metrics or information points.
            Provide the card data in JSON format:
            {{
                "title": "Clear, context-aware title",
                "metrics": [
                    {{
                        "label": "Metric Name",
                        "value": "Metric Value",
                        "trend": "up/down/stable",
                        "description": "Brief context-aware description"
                    }},
                    ...
                ],
                "summary": "Brief summary connecting metrics to conversation context",
                "footer": "Additional context or notes"
            }}
            """
            
            response = await self.gpt_service.get_chat_response(
                prompt=card_prompt,
                max_tokens=500,
                temperature=0.3
            )

            # Clean and parse the response
            response = response.replace("```json", "").replace("```", "").strip()
            card_data = json.loads(response)
            
            return {
                "has_artifact": True,
                "component_type": "Card",
                "data": {
                    "type": "card",
                    "title": card_data.get("title", "Metric Summary"),
                    "metrics": card_data.get("metrics", []),
                    "summary": card_data.get("summary", "No summary available"),
                    "footer": card_data.get("footer", ""),
                    # Add these for compatibility with artifact summary provider
                    "labels": [metric["label"] for metric in card_data.get("metrics", [])],
                    "data": {
                        "values": [metric["value"] for metric in card_data.get("metrics", [])]
                    }
                }
            }

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse card data: {e}")
            return self.generate_fallback_card()
            
        except Exception as e:
            logger.error(f"Error constructing card artifact: {str(e)}")
            return self.generate_fallback_card()

    def generate_fallback_card(self) -> Dict[str, Any]:
        """Generate a fallback card structure when card creation fails."""
        return {
            "has_artifact": True,
            "component_type": "Card",
            "data": {
                "type": "card",
                "title": "Summary Card",
                "metrics": [
                    {
                        "label": "Status",
                        "value": "No Data",
                        "trend": "stable",
                        "description": "Unable to generate metrics"
                    }
                ],
                "summary": "Failed to generate card content",
                "footer": "Please try again or contact support",
                "labels": ["Status"],
                "data": {
                    "values": ["No Data"]
                }
            }
        }

    async def construct_artifact(
        self,
        component_type: str,
        chart_type: str,
        prompt: str,
        conversation_history: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Construct the appropriate artifact based on component type.
        Now includes conversation context support.
        """
        try:
            context_summary = self._format_conversation_history(conversation_history)
            
            artifact_prompt = f"""
            Generate metadata for a {chart_type} {component_type} considering the following context:
            
            QUERY: "{prompt}"
            CONVERSATION CONTEXT: {context_summary}
            
            Generate JSON metadata for the {chart_type} {component_type}, including:
            - Title: A descriptive title based on query and context
            - Style: JSON with width and height
            - Labels: Relevant labels based on conversation context
            - Data: Appropriate numeric values
            - Source: Note that this is simulated data
            
            Respond in JSON format:
            {{
                "title": "Descriptive chart title",
                "style": {{"width": "800px", "height": "500px"}},
                "labels": ["Label1", "Label2", ...],
                "data": {{"values": [numeric values]}}
            }}
            """

            response = await self.gpt_service.get_chat_response(
                prompt=artifact_prompt,
                max_tokens=500,
                temperature=0.4
            )

            try:
                artifact_data = json.loads(response)
            except json.JSONDecodeError:
                logger.error("Failed to parse artifact response as JSON")
                artifact_data = self.generate_fallback_artifact_data()

            return {
                "has_artifact": True,
                "component_type": component_type,
                "data": {
                    "type": chart_type,
                    "title": artifact_data.get("title", "Generated Chart"),
                    "style": artifact_data.get("style", {"width": "800px", "height": "500px"}),
                    "labels": artifact_data.get("labels", ["Label1", "Label2", "Label3"]),
                    "data": artifact_data.get("data", {"values": [25, 50, 25]})
                }
            }

        except Exception as e:
            logger.error(f"Error constructing artifact: {str(e)}")
            return self.generate_fallback_artifact_data()

    def generate_fallback_artifact_data(self) -> Dict[str, Any]:
        """Generate fallback artifact data structure."""
        return {
            "title": "Generated Chart",
            "style": {"width": "800px", "height": "500px"},
            "labels": ["Category 1", "Category 2", "Category 3"],
            "data": {"values": [33, 33, 34]}
        }

