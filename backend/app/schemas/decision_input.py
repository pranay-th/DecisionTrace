"""
DecisionInput schema for user input validation.

This schema validates the initial user input when creating a new decision.
"""

from pydantic import BaseModel, Field


class DecisionInput(BaseModel):
    """
    Schema for validating user input when creating a new decision.
    
    Attributes:
        title: Brief title of the decision (5-500 characters)
        context: Detailed context and background (10-5000 characters)
        constraints: List of constraints affecting the decision
        options: List of available decision options
    """
    
    title: str = Field(
        ...,
        min_length=5,
        max_length=500,
        description="Brief title of the decision"
    )
    
    context: str = Field(
        ...,
        min_length=10,
        max_length=5000,
        description="Detailed context and background of the decision"
    )
    
    constraints: list[str] = Field(
        default_factory=list,
        description="List of constraints affecting the decision"
    )
    
    options: list[str] = Field(
        default_factory=list,
        description="List of available decision options"
    )
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "title": "Should I accept the job offer?",
                    "context": "I received an offer from Company X with a 20% salary increase, but it requires relocation to a new city.",
                    "constraints": ["Must relocate", "Salary is 20% higher", "Start date in 2 months"],
                    "options": ["Accept offer", "Decline and stay", "Negotiate terms"]
                }
            ]
        }
    }
