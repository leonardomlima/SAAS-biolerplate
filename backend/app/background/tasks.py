import asyncio

from celery import Celery
from app.core.config import settings
from app.core.database import SessionLocal
from app.services.email_service import EmailService

celery_app = Celery("tasks", broker=settings.REDIS_URL, backend=settings.REDIS_URL)


async def _run_email(template: str, kwargs: dict) -> None:
    async with SessionLocal() as session:
        email_service = EmailService()
        if template == "welcome":
            await email_service.send_welcome_email(session=session, **kwargs)
        elif template == "reset":
            await email_service.send_password_reset(session=session, **kwargs)
        elif template == "invite":
            await email_service.send_organization_invite(session=session, **kwargs)


@celery_app.task(autoretry_for=(Exception,), retry_backoff=True, retry_kwargs={"max_retries": 5})
def send_transactional_email_task(template: str, **kwargs):
    asyncio.run(_run_email(template, kwargs))
    return {"template": template, "recipient": kwargs.get("email")}
