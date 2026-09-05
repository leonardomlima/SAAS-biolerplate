"""convert timestamps to timestamptz

Revision ID: 20260401_0002
Revises: 20260401_0001
Create Date: 2026-04-01 12:00:00.000000

Converte todas as colunas TIMESTAMP para TIMESTAMP WITH TIME ZONE
para garantir consistência temporal com datetime timezone-aware (UTC).
"""

from collections.abc import Sequence

from alembic import op


revision: str = "20260401_0002"
down_revision: str | None = "20260401_0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        tables_with_timestamps = [
            "organization",
            "subscription",
            "asaascustomer",
            "asaaswebhookevent",
            "auditlog",
            "emaildelivery",
            "featureflag",
        ]
        for table in tables_with_timestamps:
            op.execute(f'ALTER TABLE "{table}" ALTER COLUMN created_at TYPE TIMESTAMP WITH TIME ZONE')
            op.execute(f'ALTER TABLE "{table}" ALTER COLUMN updated_at TYPE TIMESTAMP WITH TIME ZONE')

        op.execute('ALTER TABLE "user" ALTER COLUMN created_at TYPE TIMESTAMP WITH TIME ZONE')
        op.execute('ALTER TABLE "user" ALTER COLUMN updated_at TYPE TIMESTAMP WITH TIME ZONE')

        op.execute('ALTER TABLE "asaaswebhookevent" ALTER COLUMN received_at TYPE TIMESTAMP WITH TIME ZONE')
        op.execute('ALTER TABLE "asaaswebhookevent" ALTER COLUMN processed_at TYPE TIMESTAMP WITH TIME ZONE')

        op.execute('ALTER TABLE "user" ALTER COLUMN reset_password_expires_at TYPE TIMESTAMP WITH TIME ZONE')
        op.execute('ALTER TABLE "user" ALTER COLUMN last_login_at TYPE TIMESTAMP WITH TIME ZONE')

        op.execute('ALTER TABLE "subscription" ALTER COLUMN activated_at TYPE TIMESTAMP WITH TIME ZONE')
        op.execute('ALTER TABLE "subscription" ALTER COLUMN canceled_at TYPE TIMESTAMP WITH TIME ZONE')
        op.execute('ALTER TABLE "subscription" ALTER COLUMN last_synced_at TYPE TIMESTAMP WITH TIME ZONE')

        op.execute('ALTER TABLE "emaildelivery" ALTER COLUMN sent_at TYPE TIMESTAMP WITH TIME ZONE')


def downgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        tables_with_timestamps = [
            "organization",
            "subscription",
            "asaascustomer",
            "asaaswebhookevent",
            "auditlog",
            "emaildelivery",
            "featureflag",
        ]
        for table in tables_with_timestamps:
            op.execute(f'ALTER TABLE "{table}" ALTER COLUMN created_at TYPE TIMESTAMP')
            op.execute(f'ALTER TABLE "{table}" ALTER COLUMN updated_at TYPE TIMESTAMP')

        op.execute('ALTER TABLE "user" ALTER COLUMN created_at TYPE TIMESTAMP')
        op.execute('ALTER TABLE "user" ALTER COLUMN updated_at TYPE TIMESTAMP')
        op.execute('ALTER TABLE "asaaswebhookevent" ALTER COLUMN received_at TYPE TIMESTAMP')
        op.execute('ALTER TABLE "asaaswebhookevent" ALTER COLUMN processed_at TYPE TIMESTAMP')
        op.execute('ALTER TABLE "user" ALTER COLUMN reset_password_expires_at TYPE TIMESTAMP')
        op.execute('ALTER TABLE "user" ALTER COLUMN last_login_at TYPE TIMESTAMP')
        op.execute('ALTER TABLE "subscription" ALTER COLUMN activated_at TYPE TIMESTAMP')
        op.execute('ALTER TABLE "subscription" ALTER COLUMN canceled_at TYPE TIMESTAMP')
        op.execute('ALTER TABLE "subscription" ALTER COLUMN last_synced_at TYPE TIMESTAMP')
        op.execute('ALTER TABLE "emaildelivery" ALTER COLUMN sent_at TYPE TIMESTAMP')