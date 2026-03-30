from celery import Celery

celery_app = Celery("tasks", broker="redis://redis:6379/0")


@celery_app.task
def send_email_task(email: str):
    return email
