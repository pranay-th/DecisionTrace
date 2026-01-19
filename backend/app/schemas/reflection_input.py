"""
ReflectionInput schema for reflection request validation.

This schema validates the input when adding a reflection to a decision.
"""

from pydantic import BaseModel, Field


class ReflectionInput(BaseModel):
    """
    Schema for validating reflection input when analyzing decision outcomes.
    
    Attributes:
        actual_outcome: User-provided description of what actually happened
                       after the decision was made (minimum 20 characters)
    """
    
    actual_outcome: str = Field(
        ...,
        min_length=20,
        description="User-provided actual outcome after decision was made"
    )
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "actual_outcome": "I accepted the job offer and relocated. The new role has been challenging but rewarding, and the salary increase has significantly improved my financial situation."
                }
            ]
        }
    }
