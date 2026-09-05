import asyncio
import logging
from functools import partial

from celery import Celery
from celery.exceptions import MaxRetriesExceededError

from app.core.config import settings

logger = logging.getLogger(__name__)

celery_app = Celery("tasks", broker=settings.REDIS_URL, backend=settings.REDIS_URL)


async def _run_email(template: str, kwargs: dict) -> None:
    from app.core.database import SessionLocal
    from app.services.email_service import EmailService

    async with SessionLocal() as session:
        email_service = EmailService()
        if template == "welcome":
            await email_service.send_welcome_email(session=session, **kwargs)
        elif template == "reset":
            await email_service.send_password_reset(session=session, **kwargs)
        elif template == "invite":
            await email_service.send_organization_invite(session=session, **kwargs)


@celery_app.task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 5},
    retry_jitter=True,
)
def send_transactional_email_task(self, template: str, **kwargs):
    try:
        asyncio.run(_run_email(template, kwargs))
    except Exception as exc:
        logger.warning(f"Email task failed: {exc}, retrying...")
        try:
            raise self.retry(exc=exc)
        except MaxRetriesExceededError:
            logger.error(f"Email task failed after max retries: {template}")
            raise
    return {"template": template, "recipient": kwargs.get("email")}
