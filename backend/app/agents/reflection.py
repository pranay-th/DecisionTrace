"""
ReflectionAgent implementation.

This agent compares predicted outcomes with actual results and extracts
learning insights. It calculates accuracy scores and identifies patterns.
"""

from typing import Type, Dict, Any
import json
from pydantic import BaseModel

from app.agents.base import BaseAgent
from app.schemas.reflection_insight import ReflectionInsight


class ReflectionAgent(BaseAgent):
    """
    Agent that reflects on decision outcomes and extracts learning insights.
    
    This agent:
    - Compares predicted outcomes with actual results
    - Calculates an accuracy score (0.0 to 1.0)
    - Identifies actionable lessons learned
    - Detects repeated decision-making patterns
    
    The agent focuses on learning rather than judgment, providing
    constructive and forward-looking insights.
    """
    
    def get_system_prompt(self) -> str:
        """
        Return the system prompt for reflection.
        
        This prompt instructs the agent to compare predictions with
        actual outcomes and extract learning insights.
        
        Returns:
            System prompt string
        """
        return """You are a reflection agent. Your job is to compare predicted outcomes with actual results and extract learning insights.

Original Decision:
{decision_json}

Predicted Outcomes:
{outcome_simulations_json}

Actual Outcome:
{actual_outcome}

Analyze:
1. accuracy_score: How accurate were the predictions? (0.0 to 1.0)
2. lessons_learned: What can be learned from this decision?
3. repeated_patterns: Are there patterns from previous decisions?

Rules:
- Focus on learning, not judgment
- Be honest about prediction accuracy
- Identify actionable lessons
- Look for recurring decision-making patterns
- Keep insights constructive and forward-looking

Return ONLY valid JSON in this EXACT format (no markdown, no code blocks):
{
  "accuracy_score": 0.75,
  "lessons_learned": ["lesson 1", "lesson 2", "lesson 3"],
  "repeated_patterns": ["pattern 1", "pattern 2"]
}"""
    
    def get_response_model(self) -> Type[BaseModel]:
        """
        Return the Pydantic model for validation.
        
        Returns:
            ReflectionInsight schema class
        """
        return ReflectionInsight
    
    def _format_input(self, input_data: Dict[str, Any]) -> str:
        """
        Format input data for the prompt.
        
        Extracts the original decision, predicted outcomes, and actual outcome,
        formatting them for the LLM.
        
        Args:
            input_data: Dictionary containing 'decision', 'outcome_simulations',
                       and 'actual_outcome' keys
            
        Returns:
            Formatted input string with all inputs
        """
        decision = input_data.get('decision', {})
        outcome_simulations = input_data.get('outcome_simulations', {})
        actual_outcome = input_data.get('actual_outcome', '')
        
        # Format as pretty JSON for readability
        decision_json = json.dumps(decision, indent=2)
        outcome_simulations_json = json.dumps(outcome_simulations, indent=2)
        
        return f"""Original Decision:
{decision_json}

Predicted Outcomes:
{outcome_simulations_json}

Actual Outcome:
{actual_outcome}"""
