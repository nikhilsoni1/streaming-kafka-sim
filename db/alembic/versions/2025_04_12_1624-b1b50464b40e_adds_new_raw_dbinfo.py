"""adds_new_raw_dbinfo

Revision ID: b1b50464b40e
Revises: 2c4db5a93372
Create Date: 2025-04-12 16:24:19.455118

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b1b50464b40e'
down_revision: Union[str, None] = '2c4db5a93372'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.drop_table("raw_dbinfo", schema="dbinfo")
    op.create_table(
        "raw_dbinfo",
        sa.Column('row_id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("job_id", sa.Text, nullable=True),
        sa.Column("log_ts_utc", sa.DateTime(), nullable=True),
        sa.Column('type', sa.Text, nullable=True),
        sa.Column('log_id', sa.Text, nullable=True),
        sa.Column('rating', sa.Text, nullable=True),
        sa.Column('source', sa.Text, nullable=True),
        sa.Column('sys_hw', sa.Text, nullable=True),
        sa.Column('ver_sw', sa.Text, nullable=True),
        sa.Column('feedback', sa.Text, nullable=True),
        sa.Column('log_date', sa.Date, nullable=True),
        sa.Column('mav_type', sa.Text, nullable=True),
        sa.Column('estimator', sa.Text, nullable=True),
        sa.Column('video_url', sa.Text, nullable=True),
        sa.Column('duration_s', sa.Float, nullable=True),
        sa.Column('wind_speed', sa.Float, nullable=True),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('error_labels', sa.dialects.postgresql.JSONB, nullable=True),
        sa.Column('flight_modes', sa.dialects.postgresql.JSONB, nullable=True),
        sa.Column('vehicle_name', sa.Text, nullable=True),
        sa.Column('vehicle_uuid', sa.Text, nullable=True),
        sa.Column('airframe_name', sa.Text, nullable=True),
        sa.Column('airframe_type', sa.Text, nullable=True),
        sa.Column('ver_sw_release', sa.Text, nullable=True),
        sa.Column('sys_autostart_id', sa.Text, nullable=True),
        sa.Column('num_logged_errors', sa.Integer, nullable=True),
        sa.Column('num_logged_warnings', sa.Integer, nullable=True),
        sa.Column('flight_mode_durations', sa.dialects.postgresql.JSONB, nullable=True),
        schema='dbinfo'
    )
    


def downgrade() -> None:
    """Downgrade schema."""
    pass
