"""Seed mínimo - SQL puro, sem imports de models."""
import asyncio
import sys
from pathlib import Path
from uuid import uuid4
from datetime import datetime, timezone, timedelta

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "backend"))

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import text
from passlib.context import CryptContext
from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

async def seed_data():
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    async_session = async_sessionmaker(engine, expire_on_commit=False)
    
    print("🌱 Seed iniciado...\n")
    
    async with async_session() as session:
        try:
            tenant_id = uuid4()
            org_id = uuid4()
            now = datetime.now(timezone.utc)
            
            # 1. Organização (tabela: organization)
            result = await session.execute(
                text("SELECT id FROM organization WHERE name = :name"),
                {"name": "Empresa Teste"}
            )
            if not result.scalar_one_or_none():
                await session.execute(
                    text("""
                        INSERT INTO organization 
                        (id, tenant_id, name, is_deleted, created_at, updated_at)
                        VALUES (:id, :tenant_id, :name, false, :created_at, :updated_at)
                    """),
                    {"id": org_id, "tenant_id": tenant_id, "name": "Empresa Teste", 
                     "created_at": now, "updated_at": now}
                )
                await session.commit()
                print("✅ Organização criada")
            
            # 2. Usuário Admin (tabela: "user" - aspas necessárias)
            result = await session.execute(
                text('SELECT id FROM "user" WHERE email = :email'),
                {"email": "admin@teste.com"}
            )
            if not result.scalar_one_or_none():
                await session.execute(
                    text("""
                        INSERT INTO "user" 
                        (id, tenant_id, email, full_name, hashed_password, role, 
                         is_active, email_verified, organization_id, is_deleted, 
                         created_at, updated_at, refresh_token_version)
                        VALUES (:id, :tenant_id, :email, :full_name, :hashed_password, 
                                :role, :is_active, :email_verified, :organization_id, 
                                false, :created_at, :updated_at, 1)
                    """),
                    {
                        "id": uuid4(), "tenant_id": tenant_id,
                        "email": "admin@teste.com", "full_name": "Admin",
                        "hashed_password": hash_password("Admin@123"),
                        "role": "owner", "is_active": True,
                        "email_verified": True, "organization_id": org_id,
                        "created_at": now, "updated_at": now
                    }
                )
                await session.commit()
                print("✅ Admin criado: admin@teste.com / Admin@123")
            
            print("\n🎉 Seed concluído!")
            
        except Exception as e:
            await session.rollback()
            print(f"\n❌ ERRO: {e}")
            raise
        finally:
            await engine.dispose()

if __name__ == "__main__":
    asyncio.run(seed_data())