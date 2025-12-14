import logging
import uuid
from typing import Dict, Any

from django.template import Context, Template
from apps.core.models import EmailTemplate, User
from apps.core.tasks import send_email_async

logger = logging.getLogger(__name__)

class EmailService:
    """
    Service pour la gestion et l'envoi d'e-mails transactionnels via des templates.
    """

    @classmethod
    def _send_templated_email(
        cls,
        to_email: str,
        template_type: EmailTemplate.TemplateType,
        language: str,
        context: Dict[str, Any]
    ):
        """
        Méthode interne pour récupérer, rendre et envoyer un e-mail à partir d'un template.

        Args:
            to_email (str): Adresse e-mail du destinataire.
            template_type (EmailTemplate.TemplateType): Le type de template à utiliser.
            language (str): Le code de langue ('fr' ou 'en').
            context (Dict[str, Any]): Le contexte pour rendre le template.
        """
        try:
            template_obj = EmailTemplate.objects.get(
                template_type=template_type,
                language=language,
                active=True
            )

            # Rendu du sujet et du corps
            subject_template = Template(template_obj.subject)
            body_html_template = Template(template_obj.body_html)
            body_text_template = Template(template_obj.body_text or '')

            render_context = Context(context)

            subject = subject_template.render(render_context)
            body_html = body_html_template.render(render_context)
            body_text = body_text_template.render(render_context)

            # Appel de la tâche asynchrone
            send_email_async(
                to_email=to_email,
                subject=subject,
                body_html=body_html,
                body_text=body_text
            )

        except EmailTemplate.DoesNotExist:
            logger.error(f"Email template not found for type '{template_type}' and language '{language}'.")
        except Exception as e:
            logger.error(
                f"Failed to send '{template_type}' email to {to_email}. Error: {e}",
                exc_info=True
            )

    @classmethod
    def send_verification_email(cls, user: User, verification_url: str):
        """
        Envoie l'e-mail de vérification du compte.

        Args:
            user (User): L'utilisateur à qui envoyer l'e-mail.
            verification_url (str): L'URL pour vérifier le compte.
        """
        context = {
            'username': user.username,
            'verification_url': verification_url,
        }
        cls._send_templated_email(
            to_email=user.email,
            template_type=EmailTemplate.TemplateType.EMAIL_VERIFICATION,
            language='fr',  # Supposer le français par défaut ou adapter selon le profil utilisateur
            context=context
        )

    @classmethod
    def send_welcome_email(cls, user_email: str, username: str, institution_name: str):
        """
        Envoie l'e-mail de bienvenue à un utilisateur d'une institution.

        Args:
            user_email (str): L'email de l'utilisateur.
            username (str): Le nom de l'utilisateur.
            institution_name (str): Le nom de l'institution.
        """
        context = {
            'username': username,
            'institution_name': institution_name,
        }
        cls._send_templated_email(
            to_email=user_email,
            template_type=EmailTemplate.TemplateType.WELCOME,
            language='fr',
            context=context
        )

    @classmethod
    def send_document_revoked_email(cls, user_email: str, username: str, document_name: str, institution_name: str):
        """
        Informe un utilisateur que son document a été révoqué.

        Args:
            user_email (str): L'email de l'utilisateur.
            username (str): Le nom de l'utilisateur.
            document_name (str): Le nom ou l'identifiant du document.
            institution_name (str): Le nom de l'institution.
        """
        context = {
            'username': username,
            'document_name': document_name,
            'institution_name': institution_name,
        }
        cls._send_templated_email(
            to_email=user_email,
            template_type=EmailTemplate.TemplateType.DOCUMENT_REVOKED,
            language='fr',
            context=context
        )

    @classmethod
    def send_key_expiring_email(cls, user_email: str, username: str, key_fingerprint: str, days_remaining: int):
        """
        Alerte un utilisateur que sa clé cryptographique est sur le point d'expirer.

        Args:
            user_email (str): L'email de l'utilisateur.
            username (str): Le nom de l'utilisateur.
            key_fingerprint (str): L'empreinte de la clé.
            days_remaining (int): Le nombre de jours avant expiration.
        """
        context = {
            'username': username,
            'key_fingerprint': key_fingerprint,
            'days_remaining': days_remaining,
        }
        cls._send_templated_email(
            to_email=user_email,
            template_type=EmailTemplate.TemplateType.KEY_EXPIRING,
            language='fr',
            context=context
        )
