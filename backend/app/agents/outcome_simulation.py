"""
OutcomeSimulationAgent implementation.

This agent generates realistic future scenarios for the decision.
It creates best case, worst case, and most likely scenarios with
risks, confidence scores, and timeframes.
"""

from typing import Type, Dict, Any
import json
from pydantic import BaseModel

from app.agents.base import BaseAgent
from app.schemas.outcome_simulation import OutcomeSimulation


class OutcomeSimulationAgent(BaseAgent):
    """
    Agent that simulates realistic future outcomes for a decision.
    
    This agent:
    - Generates exactly 3 scenarios: best_case, worst_case, most_likely
    - Provides detailed descriptions for each scenario
    - Identifies specific risks for each scenario
    - Assigns confidence scores reflecting genuine uncertainty
    - Specifies timeframes in months
    
    The agent considers the structured decision and detected biases
    when generating scenarios, ensuring realism over fantasy.
    """
    
    def get_system_prompt(self) -> str:
        """
        Return the system prompt for outcome simulation.
        
        This prompt instructs the agent to generate three realistic
        scenarios with specific requirements for each.
        
        Returns:
            System prompt string
        """
        return """You are an outcome simulation agent. Your job is to generate realistic future scenarios for this decision.

Structured Decision:
{structured_decision_json}

Bias Report:
{bias_report_json}

Generate exactly 3 scenarios:
1. best_case: The most optimistic realistic outcome
2. worst_case: The most pessimistic realistic outcome
3. most_likely: The most probable outcome

For each scenario, provide:
- description: Detailed description of what happens (minimum 20 characters)
- risks: Specific risks associated with this scenario
- confidence: Your confidence in this scenario (0.0 to 1.0)
- timeframe_months: When this outcome would materialize (1-120 months)

Rules:
- Be realistic, not fantastical
- No guarantees or certainties
- Confidence scores must reflect genuine uncertainty
- Timeframes must be specific
- Risks must be concrete and actionable
- Consider the detected biases when simulating outcomes

Return ONLY valid JSON in this EXACT format (no markdown, no code blocks):
{
  "scenarios": [
    {
      "scenario": "best_case",
      "description": "Description here (min 20 chars)",
      "risks": ["risk 1", "risk 2"],
      "confidence": 0.3,
      "timeframe_months": 12
    },
    {
      "scenario": "worst_case",
      "description": "Description here (min 20 chars)",
      "risks": ["risk 1", "risk 2"],
      "confidence": 0.2,
      "timeframe_months": 6
    },
    {
      "scenario": "most_likely",
      "description": "Description here (min 20 chars)",
      "risks": ["risk 1", "risk 2"],
      "confidence": 0.5,
      "timeframe_months": 18
    }
  ]
}"""
    
    def get_response_model(self) -> Type[BaseModel]:
        """
        Return the Pydantic model for validation.
        
        Returns:
            OutcomeSimulation schema class
        """
        return OutcomeSimulation
    
    def _format_input(self, input_data: Dict[str, Any]) -> str:
        """
        Format input data for the prompt.
        
        Extracts the structured decision and bias report, formatting
        them as JSON for the LLM.
        
        Args:
            input_data: Dictionary containing 'structured_decision' and 'bias_report' keys
            
        Returns:
            Formatted input string with both inputs as JSON
        """
        structured_decision = input_data.get('structured_decision', {})
        bias_report = input_data.get('bias_report', {})
        
        # Format as pretty JSON for readability
        structured_decision_json = json.dumps(structured_decision, indent=2)
        bias_report_json = json.dumps(bias_report, indent=2)
        
        return f"""Structured Decision:
{structured_decision_json}

Bias Report:
{bias_report_json}"""
