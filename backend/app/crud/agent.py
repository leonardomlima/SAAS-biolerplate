from typing import Optional
from uuid import UUID
from sqlmodel import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.agent import Agent, ChatSession, Message, ToolDefinition
from app.crud.base import CRUDBase


class CRUDAgent(CRUDBase[Agent]):
    """CRUD para Agentes"""
    
    async def get_by_id(self, db: AsyncSession, agent_id: UUID, tenant_id: UUID) -> Optional[Agent]:
        result = await db.execute(
            select(Agent).where(Agent.id == agent_id, Agent.tenant_id == tenant_id)
        )
        return result.first()
    
    async def get_all(self, db: AsyncSession, tenant_id: UUID, limit: int = 100) -> list[Agent]:
        result = await db.execute(
            select(Agent)
            .where(Agent.tenant_id == tenant_id, Agent.is_active == True)
            .limit(limit)
        )
        return result.all()
    
    async def create(self, db: AsyncSession, obj_in: dict, tenant_id: UUID) -> Agent:
        obj_in["tenant_id"] = tenant_id
        db_obj = Agent(**obj_in)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
    
    async def update(self, db: AsyncSession, db_obj: Agent, obj_in: dict) -> Agent:
        for field, value in obj_in.items():
            setattr(db_obj, field, value)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
    
    async def delete(self, db: AsyncSession, agent_id: UUID, tenant_id: UUID) -> bool:
        result = await db.execute(
            select(Agent).where(Agent.id == agent_id, Agent.tenant_id == tenant_id)
        )
        agent = result.first()
        if agent:
            await db.delete(agent)
            await db.commit()
            return True
        return False
    
    async def get_by_model_group(self, db: AsyncSession, tenant_id: UUID, model_group: str) -> list[Agent]:
        result = await db.execute(
            select(Agent)
            .where(
                Agent.tenant_id == tenant_id,
                Agent.model_group == model_group,
                Agent.is_active == True
            )
        )
        return result.all()


class CRUDChatSession(CRUDBase[ChatSession]):
    """CRUD para Sessões de Chat"""
    
    async def get_by_id(self, db: AsyncSession, session_id: UUID, tenant_id: UUID) -> Optional[ChatSession]:
        result = await db.execute(
            select(ChatSession).where(ChatSession.id == session_id, ChatSession.tenant_id == tenant_id)
        )
        return result.first()
    
    async def get_user_sessions(
        self, 
        db: AsyncSession, 
        user_id: UUID, 
        tenant_id: UUID, 
        limit: int = 50
    ) -> list[ChatSession]:
        result = await db.execute(
            select(ChatSession)
            .where(
                ChatSession.user_id == user_id,
                ChatSession.tenant_id == tenant_id
            )
            .order_by(ChatSession.updated_at.desc())
            .limit(limit)
        )
        return result.all()
    
    async def create(self, db: AsyncSession, obj_in: dict, tenant_id: UUID) -> ChatSession:
        obj_in["tenant_id"] = tenant_id
        db_obj = ChatSession(**obj_in)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
    
    async def update_title(self, db: AsyncSession, session_id: UUID, tenant_id: UUID, title: str) -> Optional[ChatSession]:
        result = await db.execute(
            select(ChatSession).where(ChatSession.id == session_id, ChatSession.tenant_id == tenant_id)
        )
        session = result.first()
        if session:
            session.title = title
            db.add(session)
            await db.commit()
            await db.refresh(session)
        return session
    
    async def delete(self, db: AsyncSession, session_id: UUID, tenant_id: UUID) -> bool:
        result = await db.execute(
            select(ChatSession).where(ChatSession.id == session_id, ChatSession.tenant_id == tenant_id)
        )
        session = result.first()
        if session:
            await db.delete(session)
            await db.commit()
            return True
        return False


class CRUDMessage(CRUDBase[Message]):
    """CRUD para Mensagens"""
    
    async def get_session_messages(
        self, 
        db: AsyncSession, 
        session_id: UUID, 
        tenant_id: UUID,
        limit: int = 100
    ) -> list[Message]:
        result = await db.execute(
            select(Message)
            .where(
                Message.session_id == session_id,
                Message.tenant_id == tenant_id
            )
            .order_by(Message.created_at.asc())
            .limit(limit)
        )
        return result.all()
    
    async def create(self, db: AsyncSession, obj_in: dict, tenant_id: UUID) -> Message:
        obj_in["tenant_id"] = tenant_id
        db_obj = Message(**obj_in)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
    
    async def bulk_create(self, db: AsyncSession, messages: list[dict], tenant_id: UUID) -> list[Message]:
        created = []
        for msg_data in messages:
            msg_data["tenant_id"] = tenant_id
            db_obj = Message(**msg_data)
            db.add(db_obj)
            created.append(db_obj)
        
        await db.commit()
        for msg in created:
            await db.refresh(msg)
        return created


class CRUDToolDefinition(CRUDBase[ToolDefinition]):
    """CRUD para Definições de Tools"""
    
    async def get_by_name(self, db: AsyncSession, name: str, tenant_id: Optional[UUID] = None) -> Optional[ToolDefinition]:
        if tenant_id:
            result = await db.execute(
                select(ToolDefinition).where(
                    ToolDefinition.name == name,
                    (ToolDefinition.tenant_id == tenant_id) | (ToolDefinition.tenant_id == None)
                )
            )
        else:
            result = await db.execute(
                select(ToolDefinition).where(ToolDefinition.name == name)
            )
        return result.first()
    
    async def get_all_tools(self, db: AsyncSession, tenant_id: Optional[UUID] = None) -> list[ToolDefinition]:
        if tenant_id:
            result = await db.execute(
                select(ToolDefinition)
                .where(
                    (ToolDefinition.tenant_id == tenant_id) | (ToolDefinition.tenant_id == None),
                    ToolDefinition.is_active == True
                )
                .order_by(ToolDefinition.category, ToolDefinition.name)
            )
        else:
            result = await db.execute(
                select(ToolDefinition)
                .where(ToolDefinition.is_active == True)
                .order_by(ToolDefinition.category, ToolDefinition.name)
            )
        return result.all()
    
    async def create(self, db: AsyncSession, obj_in: dict) -> ToolDefinition:
        db_obj = ToolDefinition(**obj_in)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj


# Instâncias dos CRUDs
agent = CRUDAgent(Agent)
chat_session = CRUDChatSession(ChatSession)
message = CRUDMessage(Message)
tool_definition = CRUDToolDefinition(ToolDefinition)
