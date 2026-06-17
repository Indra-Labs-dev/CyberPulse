"""initial schema

Revision ID: 0001
Revises:
Create Date: 2026-06-17

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

user_role_enum = sa.Enum("ADMIN", "ANALYST", "READER", name="userrole")
severity_enum = sa.Enum("LOW", "MEDIUM", "HIGH", "CRITICAL", name="severity")
alert_type_enum = sa.Enum("CVE", "WATCHLIST", "ARTICLE", "SYSTEM", name="alerttype")
alert_status_enum = sa.Enum("NEW", "ACKNOWLEDGED", "DISMISSED", name="alertstatus")
report_type_enum = sa.Enum("CVE", "WEEKLY", "MONTHLY", name="reporttype")
report_format_enum = sa.Enum("PDF", "HTML", name="reportformat")


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("username", sa.String(100), nullable=False, unique=True),
        sa.Column("email", sa.String(255), nullable=False, unique=True),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("role", user_role_enum, nullable=False, server_default="READER"),
        sa.Column("preferences", sa.JSON(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("last_login", sa.DateTime(), nullable=True),
    )
    op.create_index("ix_users_username", "users", ["username"])
    op.create_index("ix_users_email", "users", ["email"])

    op.create_table(
        "refresh_tokens",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("jti", sa.String(36), nullable=False, unique=True),
        sa.Column("token_hash", sa.String(255), nullable=False),
        sa.Column("expires_at", sa.DateTime(), nullable=False),
        sa.Column("revoked", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_refresh_tokens_user_id", "refresh_tokens", ["user_id"])
    op.create_index("ix_refresh_tokens_jti", "refresh_tokens", ["jti"])

    op.create_table(
        "cves",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("cve_id", sa.String(32), nullable=False, unique=True),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("cvss_score", sa.Numeric(3, 1), nullable=True),
        sa.Column("cvss_vector", sa.String(255), nullable=True),
        sa.Column("severity", severity_enum, nullable=True),
        sa.Column("cwe_id", sa.String(32), nullable=True),
        sa.Column("source", sa.String(32), nullable=False, server_default="NVD"),
        sa.Column("published_at", sa.DateTime(), nullable=True),
        sa.Column("modified_at", sa.DateTime(), nullable=True),
        sa.Column("references", sa.JSON(), nullable=True),
        sa.Column("affected_products", sa.JSON(), nullable=True),
        sa.Column("exploits", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_cves_cve_id", "cves", ["cve_id"])
    op.create_index("ix_cves_cvss_score", "cves", ["cvss_score"])
    op.create_index("ix_cves_severity", "cves", ["severity"])
    op.create_index("ix_cves_source", "cves", ["source"])
    op.create_index("ix_cves_published_at", "cves", ["published_at"])

    op.create_table(
        "watchlists",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("product_name", sa.String(255), nullable=False),
        sa.Column("vendor", sa.String(255), nullable=True),
        sa.Column("version_pattern", sa.String(100), nullable=True),
        sa.Column("alert_threshold", severity_enum, nullable=False, server_default="MEDIUM"),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_watchlists_user_id", "watchlists", ["user_id"])
    op.create_index("ix_watchlists_product_name", "watchlists", ["product_name"])

    op.create_table(
        "alerts",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("cve_id", sa.Integer(), sa.ForeignKey("cves.id", ondelete="CASCADE"), nullable=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("type", alert_type_enum, nullable=False),
        sa.Column("status", alert_status_enum, nullable=False, server_default="NEW"),
        sa.Column("severity", severity_enum, nullable=False, server_default="MEDIUM"),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("acknowledged_at", sa.DateTime(), nullable=True),
    )
    op.create_index("ix_alerts_cve_id", "alerts", ["cve_id"])
    op.create_index("ix_alerts_user_id", "alerts", ["user_id"])
    op.create_index("ix_alerts_status", "alerts", ["status"])
    op.create_index("ix_alerts_severity", "alerts", ["severity"])
    op.create_index("ix_alerts_created_at", "alerts", ["created_at"])

    op.create_table(
        "reports",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("type", report_type_enum, nullable=False),
        sa.Column("format", report_format_enum, nullable=False, server_default="PDF"),
        sa.Column("file_path", sa.String(500), nullable=True),
        sa.Column("content_json", sa.JSON(), nullable=True),
        sa.Column("created_by", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_reports_type", "reports", ["type"])
    op.create_index("ix_reports_created_by", "reports", ["created_by"])
    op.create_index("ix_reports_created_at", "reports", ["created_at"])

    op.create_table(
        "scraped_articles",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("source", sa.String(255), nullable=False),
        sa.Column("source_url", sa.String(500), nullable=True),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("slug", sa.String(500), nullable=True),
        sa.Column("author", sa.String(255), nullable=True),
        sa.Column("content", sa.Text(length=4294967295).with_variant(sa.Text, "sqlite"), nullable=True),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("category", sa.String(100), nullable=True),
        sa.Column("tags", sa.JSON(), nullable=True),
        sa.Column("relevance_score", sa.Numeric(3, 2), nullable=True),
        sa.Column("mentioned_cves", sa.JSON(), nullable=True),
        sa.Column("published_at", sa.DateTime(), nullable=True),
        sa.Column("scraped_at", sa.DateTime(), nullable=False),
        sa.Column("hash", sa.String(64), nullable=False, unique=True),
        sa.Column("image_url", sa.String(500), nullable=True),
        sa.Column("read_time", sa.Integer(), nullable=True),
        sa.Column("is_favorite", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("is_read", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
    )
    op.create_index("ix_scraped_articles_source", "scraped_articles", ["source"])
    op.create_index("ix_scraped_articles_category", "scraped_articles", ["category"])
    op.create_index("ix_scraped_articles_published_at", "scraped_articles", ["published_at"])
    op.create_index("ix_scraped_articles_hash", "scraped_articles", ["hash"])
    op.execute(
        "ALTER TABLE scraped_articles ADD FULLTEXT INDEX ft_content (title, summary)"
    ) if op.get_bind().dialect.name == "mysql" else None


def downgrade() -> None:
    op.drop_table("scraped_articles")
    op.drop_table("reports")
    op.drop_table("alerts")
    op.drop_table("watchlists")
    op.drop_table("cves")
    op.drop_table("refresh_tokens")
    op.drop_table("users")
    for enum in (report_format_enum, report_type_enum, alert_status_enum, alert_type_enum, severity_enum, user_role_enum):
        enum.drop(op.get_bind(), checkfirst=True)
