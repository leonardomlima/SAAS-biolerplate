"""phase2 saas integrations schema

Revision ID: 20260330_0001
Revises:
Create Date: 2026-03-30 00:00:00.000000
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "20260330_0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "organization",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column("is_deleted", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_organization_name", "organization", ["name"])
    op.create_index("ix_organization_tenant_id", "organization", ["tenant_id"])

    op.create_table(
        "user",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column("is_deleted", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("full_name", sa.String(), nullable=True),
        sa.Column("hashed_password", sa.String(), nullable=False),
        sa.Column("organization_id", sa.Uuid(), nullable=True),
        sa.Column("role", sa.String(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("email_verified", sa.Boolean(), nullable=False),
        sa.Column("reset_password_token", sa.String(), nullable=True),
        sa.Column("reset_password_expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("email_verification_token", sa.String(), nullable=True),
        sa.Column("refresh_token_version", sa.Integer(), nullable=False),
        sa.Column("last_login_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["organization_id"], ["organization.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )
    op.create_index("ix_user_email", "user", ["email"])
    op.create_index("ix_user_role", "user", ["role"])
    op.create_index("ix_user_tenant_id", "user", ["tenant_id"])

    op.create_table(
        "subscription",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column("is_deleted", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("organization_id", sa.Uuid(), nullable=False),
        sa.Column("asaas_customer_id", sa.String(), nullable=True),
        sa.Column("asaas_subscription_id", sa.String(), nullable=True),
        sa.Column("plan_id", sa.String(), nullable=False),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("value", sa.Float(), nullable=False),
        sa.Column("billing_cycle", sa.String(), nullable=False),
        sa.Column("next_due_date", sa.Date(), nullable=True),
        sa.Column("activated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("canceled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_synced_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["organization_id"], ["organization.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("asaas_subscription_id"),
    )
    op.create_index("ix_subscription_organization_id", "subscription", ["organization_id"])
    op.create_index("ix_subscription_asaas_customer_id", "subscription", ["asaas_customer_id"])
    op.create_index("ix_subscription_asaas_subscription_id", "subscription", ["asaas_subscription_id"])
    op.create_index("ix_subscription_plan_id", "subscription", ["plan_id"])
    op.create_index("ix_subscription_status", "subscription", ["status"])
    op.create_index("ix_subscription_tenant_id", "subscription", ["tenant_id"])

    op.create_table(
        "asaascustomer",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column("is_deleted", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("organization_id", sa.Uuid(), nullable=False),
        sa.Column("asaas_customer_id", sa.String(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("cpf_cnpj", sa.String(), nullable=True),
        sa.ForeignKeyConstraint(["organization_id"], ["organization.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("asaas_customer_id"),
    )
    op.create_index("ix_asaascustomer_organization_id", "asaascustomer", ["organization_id"])
    op.create_index("ix_asaascustomer_asaas_customer_id", "asaascustomer", ["asaas_customer_id"])
    op.create_index("ix_asaascustomer_tenant_id", "asaascustomer", ["tenant_id"])

    op.create_table(
        "asaaswebhookevent",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column("is_deleted", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("organization_id", sa.Uuid(), nullable=True),
        sa.Column("event", sa.String(), nullable=False),
        sa.Column("external_id", sa.String(), nullable=True),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column("processed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("processing_status", sa.String(), nullable=False),
        sa.Column("failure_reason", sa.String(), nullable=True),
        sa.Column("received_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["organization_id"], ["organization.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("external_id"),
    )
    op.create_index("ix_asaaswebhookevent_event", "asaaswebhookevent", ["event"])
    op.create_index("ix_asaaswebhookevent_external_id", "asaaswebhookevent", ["external_id"])
    op.create_index("ix_asaaswebhookevent_processing_status", "asaaswebhookevent", ["processing_status"])
    op.create_index("ix_asaaswebhookevent_tenant_id", "asaaswebhookevent", ["tenant_id"])

    op.create_table(
        "emaildelivery",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column("is_deleted", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("template_key", sa.String(), nullable=False),
        sa.Column("recipient_email", sa.String(), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column("idempotency_key", sa.String(), nullable=False),
        sa.Column("provider_message_id", sa.String(), nullable=True),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("attempts", sa.Integer(), nullable=False),
        sa.Column("last_error", sa.String(), nullable=True),
        sa.Column("sent_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("idempotency_key"),
    )
    op.create_index("ix_emaildelivery_template_key", "emaildelivery", ["template_key"])
    op.create_index("ix_emaildelivery_recipient_email", "emaildelivery", ["recipient_email"])
    op.create_index("ix_emaildelivery_idempotency_key", "emaildelivery", ["idempotency_key"])
    op.create_index("ix_emaildelivery_status", "emaildelivery", ["status"])
    op.create_index("ix_emaildelivery_tenant_id", "emaildelivery", ["tenant_id"])


def downgrade() -> None:
    op.drop_table("emaildelivery")
    op.drop_table("asaaswebhookevent")
    op.drop_table("asaascustomer")
    op.drop_table("subscription")
    op.drop_table("user")
    op.drop_table("organization")
