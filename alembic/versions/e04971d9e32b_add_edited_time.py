"""add_edited_time

Revision ID: e04971d9e32b
Revises: 000e58dafc4b
Create Date: 2026-05-10 13:12:00.895131

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e04971d9e32b'
down_revision: Union[str, Sequence[str], None] = '000e58dafc4b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('File', sa.Column('edited_time', sa.DateTime))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('File', 'edited_time')
