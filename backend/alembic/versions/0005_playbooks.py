"""playbooks and playbook runs

Revision ID: 0005
Revises: 0004
Create Date: 2026-06-18

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0005"
down_revision: Union[str, None] = "0004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

trigger_type_enum = sa.Enum(
    "NEW_CRITICAL_CVE", "NEW_EXPLOIT", "CISA_ALERT", "MANUAL", name="playbooktriggertype"
)
scan_status_enum = sa.Enum("PENDING", "RUNNING", "COMPLETED", "FAILED", name="scanstatus")


def upgrade() -> None:
    op.create_table(
        "playbooks",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("trigger_type", trigger_type_enum, nullable=False),
        sa.Column("trigger_config", sa.JSON(), nullable=True),
        sa.Column("actions", sa.JSON(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_by", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_playbooks_trigger_type", "playbooks", ["trigger_type"])

    op.create_table(
        "playbook_runs",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("playbook_id", sa.Integer(), sa.ForeignKey("playbooks.id", ondelete="CASCADE"), nullable=False),
        sa.Column("trigger_source", sa.String(255), nullable=False),
        sa.Column("status", scan_status_enum, nullable=False, server_default="PENDING"),
        sa.Column("log", sa.Text(), nullable=True),
        sa.Column("started_at", sa.DateTime(), nullable=False),
        sa.Column("finished_at", sa.DateTime(), nullable=True),
    )
    op.create_index("ix_playbook_runs_playbook_id", "playbook_runs", ["playbook_id"])


def downgrade() -> None:
    op.drop_table("playbook_runs")
    op.drop_table("playbooks")
    trigger_type_enum.drop(op.get_bind(), checkfirst=True)
    scan_status_enum.drop(op.get_bind(), checkfirst=True)
