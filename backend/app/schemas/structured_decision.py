"""
StructuredDecision schema for DecisionStructuringAgent output.

This schema represents the structured output from the DecisionStructuringAgent,
which transforms raw user input into a clear, structured decision model.
"""

from pydantic import BaseModel, Field


class StructuredDecision(BaseModel):
    """
    Schema for structured decision output from DecisionStructuringAgent.
    
    This schema captures the structured representation of a decision after
    the agent has analyzed and organized the raw user input.
    
    Attributes:
        decision_goal: Clear statement of what needs to be decided
        constraints: All explicit and implicit constraints
        options: All available decision options
        assumptions: Hidden assumptions that have been surfaced
        missing_information: Critical information gaps identified
    """
    
    decision_goal: str = Field(
        ...,
        description="Clear, single-sentence statement of what needs to be decided"
    )
    
    constraints: list[str] = Field(
        ...,
        description="All explicit and implicit constraints affecting the decision"
    )
    
    options: list[str] = Field(
        ...,
        description="All available decision options (provided and inferred)"
    )
    
    assumptions: list[str] = Field(
        ...,
        description="Hidden assumptions that have been surfaced"
    )
    
    missing_information: list[str] = Field(
        ...,
        description="Critical information gaps that would improve the decision"
    )
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "decision_goal": "Determine whether to accept the job offer from Company X",
                    "constraints": [
                        "Must relocate to new city",
                        "Salary increase of 20%",
                        "Start date in 2 months",
                        "Current lease ends in 3 months"
                    ],
                    "options": [
                        "Accept offer and relocate",
                        "Decline offer and stay in current position",
                        "Negotiate for remote work arrangement",
                        "Negotiate for delayed start date"
                    ],
                    "assumptions": [
                        "Current job will remain stable",
                        "Relocation costs are manageable",
                        "New city has acceptable cost of living",
                        "Career growth is primary priority"
                    ],
                    "missing_information": [
                        "Total relocation costs and company support",
                        "Cost of living comparison between cities",
                        "Career growth opportunities in current role",
                        "Company culture and work-life balance at new company",
                        "Remote work policy flexibility"
                    ]
                }
            ]
        }
    }
