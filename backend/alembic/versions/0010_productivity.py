"""quick notes and task items (focus & productivity)

Revision ID: 0010
Revises: 0009
Create Date: 2026-06-18

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0010"
down_revision: Union[str, None] = "0009"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

task_status_enum = sa.Enum("TODO", "IN_PROGRESS", "DONE", name="taskstatus")
severity_enum = sa.Enum("LOW", "MEDIUM", "HIGH", "CRITICAL", name="severity")


def upgrade() -> None:
    op.create_table(
        "quick_notes",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("entity_type", sa.String(50), nullable=True),
        sa.Column("entity_id", sa.Integer(), nullable=True),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_quick_notes_user_id", "quick_notes", ["user_id"])

    op.create_table(
        "task_items",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("status", task_status_enum, nullable=False, server_default="TODO"),
        sa.Column("priority", severity_enum, nullable=False, server_default="MEDIUM"),
        sa.Column("cve_id", sa.Integer(), sa.ForeignKey("cves.id", ondelete="SET NULL"), nullable=True),
        sa.Column("due_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_task_items_user_id", "task_items", ["user_id"])
    op.create_index("ix_task_items_status", "task_items", ["status"])


def downgrade() -> None:
    op.drop_table("task_items")
    op.drop_table("quick_notes")
    task_status_enum.drop(op.get_bind(), checkfirst=True)
