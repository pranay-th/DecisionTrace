"""
BiasReport schema for BiasDetectionAgent output.

This schema represents the output from the BiasDetectionAgent, which identifies
cognitive biases that may be influencing the decision.
"""

from pydantic import BaseModel, Field


class BiasReport(BaseModel):
    """
    Schema for bias detection output from BiasDetectionAgent.
    
    This schema captures cognitive biases detected in the decision-making process,
    along with evidence and severity assessment.
    
    Attributes:
        detected_biases: List of cognitive bias names detected
        evidence: Dictionary mapping each bias to specific evidence from the decision
        severity_score: Overall bias severity score (0.0 = no bias, 1.0 = severe bias)
    """
    
    detected_biases: list[str] = Field(
        ...,
        description="List of cognitive biases detected (e.g., 'Confirmation bias', 'Status quo bias')"
    )
    
    evidence: dict[str, str] = Field(
        ...,
        description="Evidence for each detected bias, mapping bias name to specific evidence from the decision"
    )
    
    severity_score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Overall bias severity score from 0.0 (no bias) to 1.0 (severe bias)"
    )
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "detected_biases": [
                        "Status quo bias",
                        "Anchoring bias",
                        "Optimism bias"
                    ],
                    "evidence": {
                        "Status quo bias": "The decision framing emphasizes staying in the current position as a default option, with other options framed as deviations requiring justification.",
                        "Anchoring bias": "The 20% salary increase is prominently featured and may be anchoring the decision evaluation, potentially overshadowing other important factors like work-life balance or career growth.",
                        "Optimism bias": "The missing information list suggests an assumption that relocation will be manageable without fully investigating potential challenges or costs."
                    },
                    "severity_score": 0.6
                }
            ]
        }
    }
