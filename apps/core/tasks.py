import logging
from django.core.mail import send_mail
from django.conf import settings
from huey.contrib.djhuey import task

logger = logging.getLogger(__name__)

@task(retries=3)
def send_email_async(to_email: str, subject: str, body_text: str, body_html: str):
    """
    Tâche Huey pour envoyer un e-mail de manière asynchrone.
    Effectue jusqu'à 3 tentatives en cas d'échec.

    Args:
        to_email (str): L'adresse e-mail du destinataire.
        subject (str): Le sujet de l'e-mail.
        body_text (str): Le contenu de l'e-mail au format texte.
        body_html (str): Le contenu de l'e-mail au format HTML.
    """
    try:
        send_mail(
            subject=subject,
            message=body_text,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[to_email],
            html_message=body_html,
            fail_silently=False,
        )
        logger.info(f"Successfully sent email to {to_email} with subject '{subject}'")
    except Exception as e:
        logger.error(f"Failed to send email to {to_email} with subject '{subject}'. Error: {e}", exc_info=True)
        # Huey's retry mechanism will handle the re-run
        raise e
