"""alembic migration to create agent_templates table"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20260606_create_agent_templates_table'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    role_enum = postgresql.ENUM(
        'research', 'coding', 'data_analyst', 'customer_support',
        'strategic_planner', 'security_auditor', 'negotiator',
        'coordinator', 'custom', name='roleenum'
    )
    role_enum.create(op.get_bind())

    op.create_table(
        'agent_templates',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False, default=sa.text('uuid_generate_v4()')),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=80), nullable=False),
        sa.Column('role', sa.Enum('research', 'coding', 'data_aclyst', 'customer_support',
                                      'strategic_planner', 'security_auditor', 'negotiator',
                                      'coordinator', 'custom', name='roleenum'), nullable=False),
        sa.Column('description', sa.String(length=500), nullable=True),
        sa.Column('system_prompt', sa.String(length=2000), nullable=False),
        sa.Column('default_objective_template', sa.Text, nullable=True),
        sa.Column('default_tools', sa.JSON, nullable=True),
        sa.Column('default_resource_budget', sa.JSON, nullable=True),
        sa.Column('default_trust_score', sa.Float, nullable=True),
        sa.Column('personality_traits', sa.JSON, nullable=True),
        sa.Column('tags', sa.JSON, nullable=True),
        sa.Column('version', sa.String, nullable=False, server_default='1.0.0'),
        sa.Column('is_public', sa.Boolean, nullable=False, server_default=sa.text('false')),
        sa.Column('use_count', sa.Float, nullable=False, server_default='0'),
        sa.Column('avg_performance_score', sa.Float, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Index('ix_agent_templates_role', 'role'),
        sa.Index('ix_agent_templates_is_public', 'is_public'),
        sa.Index('ix_agent_templates_created_at', 'created_at')
    )

def downgrade():
    op.drop_table('agent_templates')
    role_enum = postgresql.ENUM(name='roleenum')
    role_enum.drop(op.get_bind())
