"""add agent_trust_edges table"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "b1c2d3e4f5g6"
down_revision = "314e776cf62d"
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.create_table(
        "agent_trust_edges",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("simulation_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("source_agent_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("target_agent_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("trust_score", sa.Float, nullable=False, server_default="0.0"),
        sa.Column("influence_score", sa.Float, nullable=False, server_default="0.0"),
        sa.Column("last_updated_tick", sa.Integer, nullable=False, server_default="0"),
        sa.Column("history", postgresql.JSONB, nullable=False, server_default=sa.text('"[]"')),
        sa.ForeignKeyConstraint(["simulation_id"], ["simulations.id"], ondelete="CASCADE"),
        sa.Index("ix_agent_trust_edges_sim_src_tgt", "simulation_id", "source_agent_id", "target_agent_id", unique=True),
    )

def downgrade() -> None:
    op.drop_table("agent_trust_edges")
