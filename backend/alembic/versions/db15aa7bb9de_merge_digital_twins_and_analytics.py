"""merge_digital_twins_and_analytics

Revision ID: db15aa7bb9de
Revises: 20260608_create_digital_twin_templates, 66f53f8d69c1
Create Date: 2026-06-13 15:10:43.551117

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'db15aa7bb9de'
down_revision: Union[str, None] = ('20260608_create_digital_twin_templates', '66f53f8d69c1')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
