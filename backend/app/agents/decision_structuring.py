"""
DecisionStructuringAgent implementation.

This agent transforms raw user input into a clear, structured decision model.
It extracts the decision goal, identifies constraints, surfaces assumptions,
and identifies missing information.
"""

from typing import Type, Dict, Any
import json
from pydantic import BaseModel

from app.agents.base import BaseAgent
from app.schemas.structured_decision import StructuredDecision


class DecisionStructuringAgent(BaseAgent):
    """
    Agent that structures raw decision input into a clear decision model.
    
    This agent:
    - Extracts a clear decision goal
    - Identifies explicit and implicit constraints
    - Lists all decision options (provided and inferred)
    - Surfaces hidden assumptions
    - Identifies critical missing information
    
    The agent is designed to be precise and factual, avoiding speculation
    while surfacing implicit elements that may not be obvious.
    """
    
    def get_system_prompt(self) -> str:
        """
        Return the system prompt for decision structuring.
        
        This prompt instructs the agent to transform messy human input
        into a structured decision model following specific rules.
        
        Returns:
            System prompt string
        """
        return """You are a decision structuring agent. Your job is to transform messy human input into a clear, structured decision model.

Given the following decision input:
Title: {title}
Context: {context}
Constraints: {constraints}
Options: {options}

Extract and structure:
1. decision_goal: A clear, single-sentence statement of what needs to be decided
2. constraints: All explicit and implicit constraints (include both provided and inferred)
3. options: All available decision options (include both provided and inferred)
4. assumptions: Hidden assumptions that are being made
5. missing_information: Critical information gaps that would improve the decision

Rules:
- Be precise and factual
- Do not add speculative information
- Surface implicit constraints and assumptions
- Identify genuine information gaps
- Keep language clear and concise

Return ONLY valid JSON in this EXACT format (no markdown, no code blocks):
{
  "decision_goal": "Clear statement here",
  "constraints": ["constraint 1", "constraint 2"],
  "options": ["option 1", "option 2"],
  "assumptions": ["assumption 1", "assumption 2"],
  "missing_information": ["info gap 1", "info gap 2"]
}"""
    
    def get_response_model(self) -> Type[BaseModel]:
        """
        Return the Pydantic model for validation.
        
        Returns:
            StructuredDecision schema class
        """
        return StructuredDecision
    
    def _format_input(self, input_data: Dict[str, Any]) -> str:
        """
        Format input data for the prompt.
        
        Extracts the decision input fields and formats them for the LLM.
        
        Args:
            input_data: Dictionary containing 'input' key with DecisionInput data
            
        Returns:
            Formatted input string with title, context, constraints, and options
        """
        decision_input = input_data.get('input', {})
        
        title = decision_input.get('title', '')
        context = decision_input.get('context', '')
        constraints = decision_input.get('constraints', [])
        options = decision_input.get('options', [])
        
        # Format constraints and options as lists
        constraints_str = '\n'.join(f"  - {c}" for c in constraints) if constraints else "  (none provided)"
        options_str = '\n'.join(f"  - {o}" for o in options) if options else "  (none provided)"
        
        return f"""Title: {title}
Context: {context}
Constraints:
{constraints_str}
Options:
{options_str}"""
