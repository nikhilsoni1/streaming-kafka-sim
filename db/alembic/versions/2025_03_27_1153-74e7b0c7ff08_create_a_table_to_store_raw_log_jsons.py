"""create a table to store raw log jsons

Revision ID: 74e7b0c7ff08
Revises:
Create Date: 2025-03-27 11:53:34.764667

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "74e7b0c7ff08"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "raw_dbinfo",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("log_ts_utc", sa.DateTime(), nullable=False),
        sa.Column("hash_sha256", sa.Text, unique=True, nullable=False),
        sa.Column("raw_json", sa.dialects.postgresql.JSONB, nullable=False),
        schema="dbinfo",
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("raw_dbinfo", schema="dbinfo")
