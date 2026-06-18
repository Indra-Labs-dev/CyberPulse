"""yara/sigma signature library

Revision ID: 0007
Revises: 0006
Create Date: 2026-06-18

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0007"
down_revision: Union[str, None] = "0006"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

signature_type_enum = sa.Enum("YARA", "SIGMA", name="signaturetype")


def upgrade() -> None:
    op.create_table(
        "signatures",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("type", signature_type_enum, nullable=False),
        sa.Column("rule_text", sa.Text(), nullable=False),
        sa.Column("source_description", sa.Text(), nullable=True),
        sa.Column("is_valid", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_by", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_signatures_type", "signatures", ["type"])


def downgrade() -> None:
    op.drop_table("signatures")
    signature_type_enum.drop(op.get_bind(), checkfirst=True)
