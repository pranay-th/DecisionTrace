"""
OutcomeSimulation and OutcomeScenario schemas for OutcomeSimulationAgent output.

This module defines schemas for outcome simulation, including individual scenarios
and the complete simulation output with best case, worst case, and most likely scenarios.
"""

from enum import Enum
from pydantic import BaseModel, Field


class ScenarioType(str, Enum):
    """
    Enum for scenario types in outcome simulation.
    
    Values:
        BEST_CASE: Most optimistic realistic outcome
        WORST_CASE: Most pessimistic realistic outcome
        MOST_LIKELY: Most probable outcome
    """
    
    BEST_CASE = "best_case"
    WORST_CASE = "worst_case"
    MOST_LIKELY = "most_likely"


class OutcomeScenario(BaseModel):
    """
    Schema for a single outcome scenario.
    
    Represents one possible future outcome (best case, worst case, or most likely)
    with associated details, risks, confidence, and timeframe.
    
    Attributes:
        scenario: Type of scenario (best_case, worst_case, or most_likely)
        description: Detailed description of what happens in this scenario
        risks: Specific risks associated with this scenario
        confidence: Confidence level in this scenario (0.0 to 1.0)
        timeframe_months: When this outcome would materialize (1-120 months)
    """
    
    scenario: ScenarioType = Field(
        ...,
        description="Type of scenario: best_case, worst_case, or most_likely"
    )
    
    description: str = Field(
        ...,
        min_length=20,
        description="Detailed description of what happens in this scenario"
    )
    
    risks: list[str] = Field(
        ...,
        description="Specific risks associated with this scenario"
    )
    
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Confidence level in this scenario occurring (0.0 to 1.0)"
    )
    
    timeframe_months: int = Field(
        ...,
        ge=1,
        le=120,
        description="Timeframe in months when this outcome would materialize (1-120 months)"
    )
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "scenario": "best_case",
                    "description": "You accept the offer and thrive in the new role. The 20% salary increase significantly improves your financial situation. You quickly adapt to the new city, make new friends, and find the work challenging and rewarding. Within 12 months, you receive a promotion and additional responsibilities.",
                    "risks": [
                        "Overwork leading to burnout in high-performing environment",
                        "Difficulty maintaining work-life balance in new city",
                        "High cost of living eroding salary gains"
                    ],
                    "confidence": 0.3,
                    "timeframe_months": 12
                }
            ]
        }
    }


class OutcomeSimulation(BaseModel):
    """
    Schema for complete outcome simulation with all three scenarios.
    
    This schema represents the complete output from the OutcomeSimulationAgent,
    containing exactly three scenarios: best case, worst case, and most likely.
    
    Attributes:
        scenarios: List of exactly 3 outcome scenarios
    """
    
    scenarios: list[OutcomeScenario] = Field(
        ...,
        min_length=3,
        max_length=3,
        description="List of exactly 3 scenarios: best_case, worst_case, and most_likely"
    )
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "scenarios": [
                        {
                            "scenario": "best_case",
                            "description": "You accept the offer and thrive in the new role. The 20% salary increase significantly improves your financial situation. You quickly adapt to the new city, make new friends, and find the work challenging and rewarding. Within 12 months, you receive a promotion.",
                            "risks": [
                                "Overwork leading to burnout",
                                "Difficulty maintaining work-life balance",
                                "High cost of living eroding salary gains"
                            ],
                            "confidence": 0.3,
                            "timeframe_months": 12
                        },
                        {
                            "scenario": "worst_case",
                            "description": "You accept the offer but struggle with the transition. The new company culture is toxic, and the role doesn't match expectations. Relocation costs are higher than anticipated, and you struggle to build a social network in the new city. Within 6 months, you're actively job searching again.",
                            "risks": [
                                "Financial strain from relocation and job search",
                                "Career setback from short tenure",
                                "Difficulty returning to previous market",
                                "Mental health impact from isolation and stress"
                            ],
                            "confidence": 0.2,
                            "timeframe_months": 6
                        },
                        {
                            "scenario": "most_likely",
                            "description": "You accept the offer and experience a mixed outcome. The salary increase is beneficial, but the transition is challenging. You adapt to the new role over 6-9 months, with some ups and downs. The new city takes time to feel like home, but you gradually build a social network. After 18 months, you feel settled and satisfied with the decision.",
                            "risks": [
                                "Extended adjustment period affecting performance",
                                "Homesickness and isolation in first year",
                                "Moderate financial strain during transition",
                                "Relationship strain if partner/family involved"
                            ],
                            "confidence": 0.5,
                            "timeframe_months": 18
                        }
                    ]
                }
            ]
        }
    }
