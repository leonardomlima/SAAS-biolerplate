"""drop unique constraint on asaaswebhookevent.external_id

Revision ID: 20260401_0001
Revises: 20260330_0001
Create Date: 2026-04-01 00:00:00.000000

O Asaas pode re-entregar o mesmo evento (retry policy), o que causaria
IntegrityError ao tentar inserir um registro com external_id duplicado.
Removemos a constraint UNIQUE para aceitar re-entregas de forma idempotente
no código da aplicação.
"""

from collections.abc import Sequence

from alembic import op


revision: str = "20260401_0001"
down_revision: str | None = "20260330_0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Remove a constraint UNIQUE de external_id.
    # Tenta o nome gerado pelo Alembic e o nome padrão do PostgreSQL como fallback.
    # Usando SQL direto para ser agnóstico ao nome exato da constraint.
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        # No PostgreSQL o nome padrão é <tabela>_<coluna>_key
        op.execute(
            """
            DO $$
            BEGIN
                -- tenta remover pela convenção padrão do SQLAlchemy/Alembic
                BEGIN
                    ALTER TABLE asaaswebhookevent DROP CONSTRAINT IF EXISTS uq_asaaswebhookevent_external_id;
                EXCEPTION WHEN undefined_object THEN NULL;
                END;
                -- tenta remover pelo nome padrão do PostgreSQL
                BEGIN
                    ALTER TABLE asaaswebhookevent DROP CONSTRAINT IF EXISTS asaaswebhookevent_external_id_key;
                EXCEPTION WHEN undefined_object THEN NULL;
                END;
            END
            $$;
            """
        )
    else:
        # SQLite / outros — usa batch_alter_table
        with op.batch_alter_table("asaaswebhookevent") as batch_op:
            try:
                batch_op.drop_constraint("uq_asaaswebhookevent_external_id", type_="unique")
            except Exception:
                batch_op.drop_constraint("asaaswebhookevent_external_id_key", type_="unique")


def downgrade() -> None:
    with op.batch_alter_table("asaaswebhookevent") as batch_op:
        batch_op.create_unique_constraint("uq_asaaswebhookevent_external_id", ["external_id"])
