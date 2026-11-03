import logging
import smtplib
from email.message import EmailMessage

from app.config import settings
from app.core import messages
from app.models import Task, User

logger = logging.getLogger(__name__)


def send_email(to: str, subject: str, body: str) -> None:
    if not settings.smtp_host:
        logger.info(messages.EMAIL_LOGGED, to, subject, body)
        return
    message = EmailMessage()
    message["From"] = settings.mail_from
    message["To"] = to
    message["Subject"] = subject
    message.set_content(body)
    try:
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=settings.smtp_timeout) as smtp:
            smtp.send_message(message)
    except (smtplib.SMTPException, OSError):
        logger.exception(messages.EMAIL_SEND_FAILED, to)


def comment_recipients(task: Task, author: User) -> list[str]:
    users = (task.creator, task.assignee)
    return sorted({user.email for user in users if user is not None and user.id != author.id and user.is_active})


def notify_new_comment(recipients: list[str], task_title: str, author: str, content: str) -> None:
    subject = messages.NEW_COMMENT_EMAIL_SUBJECT.format(task_title=task_title)
    body = messages.NEW_COMMENT_EMAIL_BODY.format(author=author, task_title=task_title, content=content)
    for recipient in recipients:
        send_email(recipient, subject, body)
