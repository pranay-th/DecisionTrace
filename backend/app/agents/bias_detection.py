"""
BiasDetectionAgent implementation.

This agent identifies cognitive biases that may be influencing the decision.
It detects biases with evidence-backed claims and provides a severity assessment.
"""

from typing import Type, Dict, Any
import json
from pydantic import BaseModel

from app.agents.base import BaseAgent
from app.schemas.bias_report import BiasReport


class BiasDetectionAgent(BaseAgent):
    """
    Agent that detects cognitive biases in decision-making.
    
    This agent:
    - Identifies cognitive biases (e.g., confirmation bias, status quo bias)
    - Provides specific evidence for each bias from the structured decision
    - Calculates an overall severity score
    
    The agent is conservative and evidence-based, only detecting biases
    with clear supporting evidence from the decision.
    """
    
    def get_system_prompt(self) -> str:
        """
        Return the system prompt for bias detection.
        
        This prompt instructs the agent to identify cognitive biases
        with evidence-backed claims and severity assessment.
        
        Returns:
            System prompt string
        """
        return """You are a cognitive bias detection agent. Your job is to identify biases that may be influencing this decision.

Structured Decision:
{structured_decision_json}

Analyze this decision for cognitive biases. Common biases include:
- Confirmation bias: Seeking information that confirms existing beliefs
- Anchoring bias: Over-relying on the first piece of information
- Status quo bias: Preferring things to stay the same
- Sunk cost fallacy: Continuing based on past investment
- Availability heuristic: Overweighting recent or memorable information
- Optimism bias: Overestimating positive outcomes

For each bias detected:
1. Name the bias
2. Provide specific evidence from the decision that demonstrates this bias
3. Calculate an overall severity_score (0.0 to 1.0)

Rules:
- Only detect biases with clear evidence
- Do not diagnose mental states
- Be conservative with severity scores
- Evidence must reference specific elements from the structured decision
- If no biases are detected, return empty list with severity_score 0.0

Return ONLY valid JSON in this EXACT format (no markdown, no code blocks):
{
  "detected_biases": ["Bias Name 1", "Bias Name 2"],
  "evidence": {
    "Bias Name 1": "Evidence text here",
    "Bias Name 2": "Evidence text here"
  },
  "severity_score": 0.5
}"""
    
    def get_response_model(self) -> Type[BaseModel]:
        """
        Return the Pydantic model for validation.
        
        Returns:
            BiasReport schema class
        """
        return BiasReport
    
    def _format_input(self, input_data: Dict[str, Any]) -> str:
        """
        Format input data for the prompt.
        
        Extracts the structured decision and formats it as JSON for the LLM.
        
        Args:
            input_data: Dictionary containing 'structured_decision' key
            
        Returns:
            Formatted input string with structured decision as JSON
        """
        structured_decision = input_data.get('structured_decision', {})
        
        # Format as pretty JSON for readability
        structured_decision_json = json.dumps(structured_decision, indent=2)
        
        return f"""Structured Decision:
{structured_decision_json}"""
