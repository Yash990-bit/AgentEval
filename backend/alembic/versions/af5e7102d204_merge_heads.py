"""merge heads

Revision ID: af5e7102d204
Revises: 20260606_create_agent_templates_table, b1c2d3e4f5g6
Create Date: 2026-06-08 20:34:12.385590

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'af5e7102d204'
down_revision: Union[str, None] = ('20260606_create_agent_templates_table', 'b1c2d3e4f5g6')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
