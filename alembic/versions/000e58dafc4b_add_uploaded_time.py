"""add_uploaded_time

Revision ID: 000e58dafc4b
Revises:
Create Date: 2026-05-10 13:04:53.397575

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "000e58dafc4b"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column("File", sa.Column("uploaded_time", sa.DateTime))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("File", "uploaded_time")
