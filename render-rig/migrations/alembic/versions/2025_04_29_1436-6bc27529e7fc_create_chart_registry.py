"""create chart registry

Revision ID: 6bc27529e7fc
Revises:
Create Date: 2025-04-29 14:36:43.943276

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "6bc27529e7fc"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "chart_registry",
        sa.Column("log_ts_utc", sa.DateTime(), nullable=False),
        sa.Column("upd_ts_utc", sa.DateTime(), nullable=False),
        sa.Column("log_id", sa.Text, nullable=False, primary_key=True),
        sa.Column("chart_id", sa.Text, nullable=False),
        sa.Column("chart_name", sa.Text, nullable=False, primary_key=True),
        sa.Column("chart_hash_sha256", sa.Text, nullable=False),
        sa.Column("bucket_name", sa.Text, nullable=False),
        sa.Column("key", sa.Text, nullable=False),
        schema="registry",
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("chart_registry", schema="registry")
