"""Initial schema for identity service."""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import ARRAY, JSONB

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("email", sa.String(255), unique=True, nullable=False, index=True),
        sa.Column("email_verified", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("phone", sa.String(32), unique=True, nullable=True, index=True),
        sa.Column("phone_verified", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true", index=True),
        sa.Column("is_locked", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("locked_until", sa.DateTime(timezone=True), nullable=True),
        sa.Column("failed_login_attempts", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("last_login_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_login_ip", sa.String(64), nullable=True),
        sa.Column("primary_role", sa.String(64), nullable=False, index=True),
        sa.Column("roles", ARRAY(sa.String()), nullable=False, server_default="{}"),
        sa.Column("organization_id", sa.String(36), nullable=True, index=True),
        sa.Column("assigned_stores", ARRAY(sa.String()), nullable=False, server_default="{}"),
        sa.Column("assigned_jurisdictions", ARRAY(sa.String()), nullable=False, server_default="{}"),
        sa.Column("consumer_level", sa.String(32), nullable=True, index=True),
        sa.Column("seller_level", sa.String(32), nullable=True, index=True),
        sa.Column("trust_score", sa.Integer(), nullable=False, server_default="50", index=True),
        sa.Column("risk_score", sa.Integer(), nullable=False, server_default="0", index=True),
        sa.Column("mfa_enabled", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("mfa_method", sa.String(32), nullable=True),
        sa.Column("mfa_secret_encrypted", sa.Text(), nullable=True),
        sa.Column("mfa_backup_codes_hashed", ARRAY(sa.String()), nullable=False, server_default="{}"),
        sa.Column("mfa_enrolled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("locale", sa.String(10), nullable=False, server_default="en"),
        sa.Column("timezone", sa.String(64), nullable=False, server_default="UTC"),
        sa.Column("metadata_json", JSONB(), nullable=False, server_default="{}"),
        sa.Column("consumer_id", sa.String(36), nullable=True, index=True),
        sa.Column("retailer_id", sa.String(36), nullable=True, index=True),
        sa.Column("driver_id", sa.String(36), nullable=True, index=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_users_role_active", "users", ["primary_role", "is_active"])
    op.create_index("ix_users_org_role", "users", ["organization_id", "primary_role"])

    op.create_table(
        "sessions",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("refresh_token_hash", sa.String(128), unique=True, nullable=False, index=True),
        sa.Column("token_family_id", sa.String(64), nullable=False, index=True),
        sa.Column("access_jti", sa.String(64), nullable=True),
        sa.Column("ip_address", sa.String(64), nullable=False),
        sa.Column("user_agent", sa.Text(), nullable=False),
        sa.Column("device_id", sa.String(36), nullable=True, index=True),
        sa.Column("geo_country", sa.String(2), nullable=True),
        sa.Column("geo_state", sa.String(64), nullable=True),
        sa.Column("geo_city", sa.String(128), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true", index=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False, index=True),
        sa.Column("absolute_expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("revoked_reason", sa.String(64), nullable=True),
        sa.Column("last_used_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        "devices",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("device_fingerprint", sa.String(128), nullable=False, index=True),
        sa.Column("device_name", sa.String(128), nullable=True),
        sa.Column("device_type", sa.String(32), nullable=True),
        sa.Column("os", sa.String(64), nullable=True),
        sa.Column("browser", sa.String(64), nullable=True),
        sa.Column("is_trusted", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("trust_score", sa.Integer(), nullable=False, server_default="50"),
        sa.Column("first_seen_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("last_seen_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("last_ip", sa.String(64), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        "api_keys",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("organization_id", sa.String(36), nullable=True, index=True),
        sa.Column("name", sa.String(128), nullable=False),
        sa.Column("key_id", sa.String(32), unique=True, nullable=False, index=True),
        sa.Column("key_hash", sa.String(128), unique=True, nullable=False, index=True),
        sa.Column("key_prefix", sa.String(16), nullable=False),
        sa.Column("scopes", ARRAY(sa.String()), nullable=False, server_default="{}"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true", index=True),
        sa.Column("last_used_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        "role_definitions",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("name", sa.String(64), unique=True, nullable=False, index=True),
        sa.Column("display_name", sa.String(128), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("domain", sa.String(32), nullable=False, index=True),
        sa.Column("level", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("parent_roles", ARRAY(sa.String()), nullable=False, server_default="{}"),
        sa.Column("permissions", ARRAY(sa.String()), nullable=False, server_default="{}"),
        sa.Column("is_system", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        "password_reset_tokens",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("token_hash", sa.String(128), unique=True, nullable=False, index=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("used_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("ip_address", sa.String(64), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        "email_verification_tokens",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("token_hash", sa.String(128), unique=True, nullable=False, index=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("used_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("email_verification_tokens")
    op.drop_table("password_reset_tokens")
    op.drop_table("role_definitions")
    op.drop_table("api_keys")
    op.drop_table("devices")
    op.drop_table("sessions")
    op.drop_table("users")
