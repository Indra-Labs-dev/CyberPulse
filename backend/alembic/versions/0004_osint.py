"""osint results

Revision ID: 0004
Revises: 0003
Create Date: 2026-06-18

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0004"
down_revision: Union[str, None] = "0003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

osint_type_enum = sa.Enum(
    "EMAIL_BREACH", "IP_LOOKUP", "DOMAIN_LOOKUP", "GITHUB_DORK", "PASTEBIN", "CERT_TRANSPARENCY",
    name="osinttype",
)


def upgrade() -> None:
    op.create_table(
        "osint_results",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("type", osint_type_enum, nullable=False),
        sa.Column("target", sa.String(500), nullable=False),
        sa.Column("result", sa.JSON(), nullable=True),
        sa.Column("source", sa.String(100), nullable=False),
        sa.Column("scanned_at", sa.DateTime(), nullable=False),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
    )
    op.create_index("ix_osint_results_type", "osint_results", ["type"])
    op.create_index("ix_osint_results_target", "osint_results", ["target"])
    op.create_index("ix_osint_results_scanned_at", "osint_results", ["scanned_at"])


def downgrade() -> None:
    op.drop_table("osint_results")
    osint_type_enum.drop(op.get_bind(), checkfirst=True)
