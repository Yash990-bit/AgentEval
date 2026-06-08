"""create_analytics_and_metrics_tables

Revision ID: 66f53f8d69c1
Revises: af5e7102d204
Create Date: 2026-06-08 20:34:15.916231

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '66f53f8d69c1'
down_revision: Union[str, None] = 'af5e7102d204'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create simulation_analytics table
    op.create_table(
        'simulation_analytics',
        sa.Column('simulation_id', sa.UUID(), primary_key=True, nullable=False),
        sa.Column('total_ticks_run', sa.Integer(), nullable=False),
        sa.Column('total_agents', sa.Integer(), nullable=False),
        sa.Column('total_goals', sa.Integer(), nullable=False),
        sa.Column('overall_success_rate', sa.Float(), nullable=False),
        sa.Column('overall_failure_rate', sa.Float(), nullable=False),
        sa.Column('avg_efficiency_score', sa.Float(), nullable=False),
        sa.Column('avg_trust_score', sa.Float(), nullable=False),
        sa.Column('avg_intelligence_score', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('avg_cooperation_score', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('avg_reliability_score', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('avg_risk_score', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('total_conflicts_detected', sa.Integer(), nullable=False),
        sa.Column('conflicts_auto_resolved', sa.Integer(), nullable=False),
        sa.Column('conflicts_escalated', sa.Integer(), nullable=False),
        sa.Column('total_emergent_behaviors', sa.Integer(), nullable=False),
        sa.Column('total_resource_units_consumed', sa.JSON(), nullable=False),
        sa.Column('total_waste_rate', sa.Float(), nullable=False),
        sa.Column('top_performing_agent_id', sa.UUID(), nullable=True),
        sa.Column('most_conflicted_agent_id', sa.UUID(), nullable=True),
        sa.Column('completion_status', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )
    op.create_index('ix_simulation_analytics_simulation_id', 'simulation_analytics', ['simulation_id'])

    # Create agent_performance_metrics table
    op.create_table(
        'agent_performance_metrics',
        sa.Column('id', sa.UUID(), primary_key=True, nullable=False),
        sa.Column('agent_id', sa.UUID(), nullable=False),
        sa.Column('simulation_id', sa.UUID(), nullable=False),
        sa.Column('goals_completed', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('goals_failed', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('goals_abandoned', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('success_rate', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('efficiency_score', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('cooperation_score', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('reliability_score', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('intelligence_score', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('risk_score', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('composite_score', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('messages_sent', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('messages_received', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('resource_utilization_pct', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('avg_trust_given', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('avg_trust_received', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('failure_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('conflict_involvement_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('overall_rank', sa.Integer(), nullable=False, server_default='0'),
    )


def downgrade() -> None:
    op.drop_table('agent_performance_metrics')
    op.drop_index('ix_simulation_analytics_simulation_id', table_name='simulation_analytics')
    op.drop_table('simulation_analytics')
