"""adds_log_dl_reg

Revision ID: 2c4db5a93372
Revises: 8d3215844610
Create Date: 2025-04-11 16:34:09.977081

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2c4db5a93372'
down_revision: Union[str, None] = '8d3215844610'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "logs_dl_reg",
        sa.Column("id", sa.Integer, autoincrement=True, primary_key=True),
        sa.Column("job_id", sa.Text, nullable=True),
        sa.Column("log_ts_utc", sa.DateTime(), nullable=True),
        sa.Column("upd_ts_utc", sa.DateTime(), nullable=True),
        sa.Column("log_id", sa.Text, primary_key=True),
        sa.Column("status", sa.Text, nullable=True),
        sa.Column("file_s3_path", sa.Text, nullable=True),
        sa.Column("file_name", sa.Text, nullable=True),
        sa.Column("file_ext", sa.Text, nullable=True),
        sa.Column("file_size_bytes", sa.BigInteger, nullable=True),
        sa.Column("file_sha256", sa.Text, nullable=True),
        sa.Column("stdout", sa.Text, nullable=True),
        sa.Column("stderr", sa.Text, nullable=True),
        schema="registry"
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("logs_dl_reg", schema="registry")
