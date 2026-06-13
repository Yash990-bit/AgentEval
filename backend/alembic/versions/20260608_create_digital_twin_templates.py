"""alembic revision to create digital_twin_templates table"""

from alembic import op
import sqlalchemy as sa
import sqlalchemy.dialects.postgresql as pg

# revision identifiers, used by Alembic.
revision = "20260608_create_digital_twin_templates"
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        "digital_twin_templates",
        sa.Column("id", pg.UUID(as_uuid=True), primary_key=True, nullable=False, default=sa.text("gen_random_uuid()")),
        sa.Column("name", sa.String, nullable=False, unique=True),
        sa.Column("industry", sa.String, nullable=False),
        sa.Column("twin_type", sa.Enum(
            "support_team",
            "dev_team",
            "sales_team",
            "ops_team",
            "research_lab",
            "trading_desk",
            "security_team",
            "custom",
            name="twintype"
        ), nullable=False),
        sa.Column("org_structure", sa.JSON, nullable=False),
        sa.Column("default_agent_count", sa.Integer, nullable=False),
        sa.Column("default_scenario_config", sa.JSON, nullable=False),
        sa.Column("real_world_kpis", sa.JSON, nullable=False),
        sa.Column("is_public", sa.Boolean, nullable=False, server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )

def downgrade():
    op.drop_table("digital_twin_templates")
