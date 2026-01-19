"""
ReflectionInsight schema for ReflectionAgent output.

This schema represents the output from the ReflectionAgent, which compares
predicted outcomes with actual results and extracts learning insights.
"""

from pydantic import BaseModel, Field


class ReflectionInsight(BaseModel):
    """
    Schema for reflection insight output from ReflectionAgent.
    
    This schema captures the analysis of how predicted outcomes compared to
    actual results, along with lessons learned and patterns identified.
    
    Attributes:
        accuracy_score: How accurate the predictions were (0.0 to 1.0)
        lessons_learned: List of actionable lessons from this decision
        repeated_patterns: List of recurring decision-making patterns identified
    """
    
    accuracy_score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Accuracy score comparing predictions to actual outcome (0.0 = completely inaccurate, 1.0 = perfectly accurate)"
    )
    
    lessons_learned: list[str] = Field(
        ...,
        min_length=1,
        description="Actionable lessons learned from this decision and its outcome"
    )
    
    repeated_patterns: list[str] = Field(
        default_factory=list,
        description="Recurring decision-making patterns identified across multiple decisions"
    )
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "accuracy_score": 0.75,
                    "lessons_learned": [
                        "The salary increase was beneficial as predicted, but the adjustment period was longer than anticipated",
                        "Company culture research before accepting offers is critical - the toxic environment was not apparent during interviews",
                        "Building a social network in a new city requires more proactive effort than assumed",
                        "The 'most likely' scenario was closest to reality, suggesting the simulation was well-calibrated"
                    ],
                    "repeated_patterns": [
                        "Tendency to underweight cultural fit in favor of financial considerations",
                        "Optimism bias when estimating adaptation timelines",
                        "Insufficient research on cost of living and quality of life factors"
                    ]
                }
            ]
        }
    }
