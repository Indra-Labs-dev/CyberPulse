"""mitre attack mapping + incident management

Revision ID: 0002
Revises: 0001
Create Date: 2026-06-18

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0002"
down_revision: Union[str, None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

incident_status_enum = sa.Enum(
    "DETECTION", "ANALYSIS", "CONTAINMENT", "ERADICATION", "RECOVERY", "LESSONS_LEARNED", "CLOSED",
    name="incidentstatus",
)


def upgrade() -> None:
    op.create_table(
        "attack_techniques",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("technique_id", sa.String(16), nullable=False, unique=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("tactic", sa.String(64), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
    )
    op.create_index("ix_attack_techniques_technique_id", "attack_techniques", ["technique_id"])
    op.create_index("ix_attack_techniques_tactic", "attack_techniques", ["tactic"])

    op.create_table(
        "cve_attack_mappings",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("cve_id", sa.Integer(), sa.ForeignKey("cves.id", ondelete="CASCADE"), nullable=False),
        sa.Column(
            "technique_id", sa.Integer(), sa.ForeignKey("attack_techniques.id", ondelete="CASCADE"), nullable=False
        ),
        sa.Column("confidence", sa.Numeric(3, 2), nullable=False, server_default="0.5"),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_cve_attack_mappings_cve_id", "cve_attack_mappings", ["cve_id"])
    op.create_index("ix_cve_attack_mappings_technique_id", "cve_attack_mappings", ["technique_id"])

    op.create_table(
        "incidents",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column(
            "severity",
            sa.Enum("LOW", "MEDIUM", "HIGH", "CRITICAL", name="severity"),
            nullable=False,
            server_default="MEDIUM",
        ),
        sa.Column("status", incident_status_enum, nullable=False, server_default="DETECTION"),
        sa.Column("assigned_to", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("cve_id", sa.Integer(), sa.ForeignKey("cves.id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_by", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("resolved_at", sa.DateTime(), nullable=True),
        sa.Column("resolution_notes", sa.Text(), nullable=True),
    )
    op.create_index("ix_incidents_severity", "incidents", ["severity"])
    op.create_index("ix_incidents_status", "incidents", ["status"])
    op.create_index("ix_incidents_created_at", "incidents", ["created_at"])

    op.create_table(
        "incident_activities",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("incident_id", sa.Integer(), sa.ForeignKey("incidents.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("action", sa.String(100), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_incident_activities_incident_id", "incident_activities", ["incident_id"])


def downgrade() -> None:
    op.drop_table("incident_activities")
    op.drop_table("incidents")
    op.drop_table("cve_attack_mappings")
    op.drop_table("attack_techniques")
    incident_status_enum.drop(op.get_bind(), checkfirst=True)
