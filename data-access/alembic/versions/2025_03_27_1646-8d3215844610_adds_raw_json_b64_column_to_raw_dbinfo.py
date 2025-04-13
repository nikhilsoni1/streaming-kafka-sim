"""adds raw_json_b64 column to raw_dbinfo

Revision ID: 8d3215844610
Revises: 74e7b0c7ff08
Create Date: 2025-03-27 16:46:34.039407

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "8d3215844610"
down_revision: Union[str, None] = "74e7b0c7ff08"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # sa.Column("hash_sha256", sa.Text, unique=True, nullable=False)
    op.add_column(
        "raw_dbinfo",
        sa.Column("raw_json_b64", sa.Text, nullable=False),
        schema="dbinfo",
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("raw_dbinfo", "raw_json_b64", schema="dbinfo")
