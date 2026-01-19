"""Initial schema with decisions table

Revision ID: 6425a63343f6
Revises: 
Create Date: 2026-01-19 21:58:40.745638

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = '6425a63343f6'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create decisions table
    op.create_table(
        'decisions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('title', sa.String(length=500), nullable=False),
        sa.Column('context', sa.Text(), nullable=False),
        sa.Column('constraints', postgresql.ARRAY(sa.Text()), nullable=True),
        sa.Column('options', postgresql.ARRAY(sa.Text()), nullable=True),
        sa.Column('structured_decision', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('bias_report', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('outcome_simulations', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('reflection_insight', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('actual_outcome', sa.Text(), nullable=True),
        sa.Column('actual_outcome_date', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('execution_log', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes
    op.create_index(
        'idx_decisions_created_at',
        'decisions',
        ['created_at'],
        unique=False,
        postgresql_ops={'created_at': 'DESC'}
    )
    op.create_index(
        'idx_decisions_updated_at',
        'decisions',
        ['updated_at'],
        unique=False,
        postgresql_ops={'updated_at': 'DESC'}
    )


def downgrade() -> None:
    # Drop indexes
    op.drop_index('idx_decisions_updated_at', table_name='decisions')
    op.drop_index('idx_decisions_created_at', table_name='decisions')
    
    # Drop table
    op.drop_table('decisions')
