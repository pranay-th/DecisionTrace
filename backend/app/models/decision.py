"""
Decision Model

SQLAlchemy model for storing decisions and their analysis results.
"""

from sqlalchemy import Column, String, Text, TIMESTAMP, Index, ARRAY
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
import uuid

from app.database import Base


class Decision(Base):
    """
    Decision model for storing user decisions and agent analysis results.
    
    Stores:
    - User input (title, context, constraints, options)
    - Agent outputs (structured_decision, bias_report, outcome_simulations, reflection_insight)
    - Execution metadata (execution_log, timestamps)
    - Actual outcome data (for reflection)
    """
    
    __tablename__ = "decisions"
    
    # Primary key
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
        comment="Unique identifier for the decision"
    )
    
    # Timestamps
    created_at = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=func.now(),
        comment="Timestamp when the decision was created"
    )
    
    updated_at = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
        comment="Timestamp when the decision was last updated"
    )
    
    # User input fields
    title = Column(
        String(500),
        nullable=False,
        comment="Short title describing the decision"
    )
    
    context = Column(
        Text,
        nullable=False,
        comment="Detailed context and background for the decision"
    )
    
    constraints = Column(
        ARRAY(Text),
        nullable=True,
        default=[],
        comment="List of constraints affecting the decision"
    )
    
    options = Column(
        ARRAY(Text),
        nullable=True,
        default=[],
        comment="List of available decision options"
    )
    
    # Agent output fields (JSONB for flexibility)
    structured_decision = Column(
        JSONB,
        nullable=True,
        comment="Output from DecisionStructuringAgent (StructuredDecision schema)"
    )
    
    bias_report = Column(
        JSONB,
        nullable=True,
        comment="Output from BiasDetectionAgent (BiasReport schema)"
    )
    
    outcome_simulations = Column(
        JSONB,
        nullable=True,
        comment="Output from OutcomeSimulationAgent (array of 3 OutcomeScenario objects)"
    )
    
    reflection_insight = Column(
        JSONB,
        nullable=True,
        comment="Output from ReflectionAgent (ReflectionInsight schema)"
    )
    
    # Actual outcome data (for reflection)
    actual_outcome = Column(
        Text,
        nullable=True,
        comment="User-provided actual outcome after decision was made"
    )
    
    actual_outcome_date = Column(
        TIMESTAMP(timezone=True),
        nullable=True,
        comment="Timestamp when actual outcome was recorded"
    )
    
    # Execution metadata
    execution_log = Column(
        JSONB,
        nullable=True,
        comment="Log of agent execution details (timestamps, models used, errors)"
    )
    
    # Indexes for common queries
    __table_args__ = (
        Index('idx_decisions_created_at', 'created_at', postgresql_ops={'created_at': 'DESC'}),
        Index('idx_decisions_updated_at', 'updated_at', postgresql_ops={'updated_at': 'DESC'}),
    )
    
    def __repr__(self) -> str:
        """String representation of Decision."""
        return f"<Decision(id={self.id}, title='{self.title[:50]}...', created_at={self.created_at})>"
    
    def to_dict(self) -> dict:
        """
        Convert Decision model to dictionary.
        
        Returns:
            dict: Dictionary representation of the decision
        """
        return {
            "id": str(self.id),
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "title": self.title,
            "context": self.context,
            "constraints": self.constraints or [],
            "options": self.options or [],
            "structured_decision": self.structured_decision,
            "bias_report": self.bias_report,
            "outcome_simulations": self.outcome_simulations,
            "reflection_insight": self.reflection_insight,
            "actual_outcome": self.actual_outcome,
            "actual_outcome_date": self.actual_outcome_date.isoformat() if self.actual_outcome_date else None,
            "execution_log": self.execution_log or [],
        }
    
    @property
    def has_reflection(self) -> bool:
        """Check if decision has reflection insight."""
        return self.reflection_insight is not None
