"""create_api_keys_and_members_tables

Revision ID: 857b92ec32f1
Revises: db15aa7bb9de
Create Date: 2026-06-13 15:10:56.241514

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '857b92ec32f1'
down_revision: Union[str, None] = 'db15aa7bb9de'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # Create api_keys table
    op.create_table('api_keys',
        sa.Column('id', sa.String(length=50), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('scopes', sa.String(length=50), nullable=False),
        sa.Column('created', sa.String(length=50), nullable=False),
        sa.Column('last_used', sa.String(length=50), nullable=False),
        sa.Column('requests', sa.String(length=50), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('value', sa.String(length=100), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('value')
    )
    
    # Create members table
    op.create_table('members',
        sa.Column('id', sa.String(length=50), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('role', sa.String(length=50), nullable=False),
        sa.Column('last_active', sa.String(length=50), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

def downgrade() -> None:
    op.drop_table('members')
    op.drop_table('api_keys')
