"""threat correlation: actors, campaigns, cve/article links

Revision ID: 0003
Revises: 0002
Create Date: 2026-06-18

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0003"
down_revision: Union[str, None] = "0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

campaign_status_enum = sa.Enum("ACTIVE", "CONTAINED", "RESOLVED", name="campaignstatus")


def upgrade() -> None:
    op.create_table(
        "threat_actors",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(255), nullable=False, unique=True),
        sa.Column("aliases", sa.JSON(), nullable=True),
        sa.Column("country", sa.String(100), nullable=True),
        sa.Column("motivation", sa.String(100), nullable=True),
        sa.Column("ttps", sa.JSON(), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )

    op.create_table(
        "campaigns",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("actor_id", sa.Integer(), sa.ForeignKey("threat_actors.id", ondelete="SET NULL"), nullable=True),
        sa.Column("threat_score", sa.Numeric(4, 1), nullable=False, server_default="0"),
        sa.Column("status", campaign_status_enum, nullable=False, server_default="ACTIVE"),
        sa.Column("first_seen", sa.DateTime(), nullable=True),
        sa.Column("last_seen", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_campaigns_status", "campaigns", ["status"])

    op.create_table(
        "campaign_cves",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("campaign_id", sa.Integer(), sa.ForeignKey("campaigns.id", ondelete="CASCADE"), nullable=False),
        sa.Column("cve_id", sa.Integer(), sa.ForeignKey("cves.id", ondelete="CASCADE"), nullable=False),
    )
    op.create_index("ix_campaign_cves_campaign_id", "campaign_cves", ["campaign_id"])
    op.create_index("ix_campaign_cves_cve_id", "campaign_cves", ["cve_id"])

    op.create_table(
        "campaign_articles",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("campaign_id", sa.Integer(), sa.ForeignKey("campaigns.id", ondelete="CASCADE"), nullable=False),
        sa.Column(
            "article_id", sa.Integer(), sa.ForeignKey("scraped_articles.id", ondelete="CASCADE"), nullable=False
        ),
    )
    op.create_index("ix_campaign_articles_campaign_id", "campaign_articles", ["campaign_id"])
    op.create_index("ix_campaign_articles_article_id", "campaign_articles", ["article_id"])


def downgrade() -> None:
    op.drop_table("campaign_articles")
    op.drop_table("campaign_cves")
    op.drop_table("campaigns")
    op.drop_table("threat_actors")
    campaign_status_enum.drop(op.get_bind(), checkfirst=True)
