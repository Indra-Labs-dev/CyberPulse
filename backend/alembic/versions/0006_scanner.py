"""lightweight vulnerability scanner

Revision ID: 0006
Revises: 0005
Create Date: 2026-06-18

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0006"
down_revision: Union[str, None] = "0005"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

scan_type_enum = sa.Enum("PORT_SCAN", "FILE_SCAN", name="scantype")
scan_status_enum = sa.Enum("PENDING", "RUNNING", "COMPLETED", "FAILED", name="scanstatus")


def upgrade() -> None:
    op.create_table(
        "vuln_scans",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("target", sa.String(255), nullable=False),
        sa.Column("scan_type", scan_type_enum, nullable=False),
        sa.Column("status", scan_status_enum, nullable=False, server_default="PENDING"),
        sa.Column("findings", sa.JSON(), nullable=True),
        sa.Column("schedule_minutes", sa.Integer(), nullable=True),
        sa.Column("created_by", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
    )
    op.create_index("ix_vuln_scans_target", "vuln_scans", ["target"])
    op.create_index("ix_vuln_scans_scan_type", "vuln_scans", ["scan_type"])
    op.create_index("ix_vuln_scans_created_at", "vuln_scans", ["created_at"])


def downgrade() -> None:
    op.drop_table("vuln_scans")
    scan_type_enum.drop(op.get_bind(), checkfirst=True)
