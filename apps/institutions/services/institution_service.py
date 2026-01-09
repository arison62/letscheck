import logging
from datetime import datetime
from typing import Dict, Any, Optional

from django.db import transaction
from django.utils import timezone
from django.http import HttpRequest
from django.core import signing
from django.urls import reverse

from apps.core.models import User
from apps.core.services.audit_service import AuditService
from apps.core.services.email_service import EmailService
from apps.institutions.models import Institution, InstitutionUser

logger = logging.getLogger(__name__)

class InstitutionService:
    """
    Service pour la gestion de la logique métier des institutions.
    """

    @classmethod
    @transaction.atomic
    def validate_institution(cls, institution: Institution, admin_user: User, request: HttpRequest):
        """
        Valide une institution en attente.

        Args:
            institution (Institution): L'institution à valider.
            admin_user (User): L'administrateur qui effectue la validation.
            request (HttpRequest): The Django request object.
        """
        if institution.status != Institution.Status.PENDING:
            logger.warning(f"Attempted to validate an institution that is not pending: {institution.id}")
            return

        institution.status = Institution.Status.ACTIVE
        institution.validated_by = admin_user
        institution.validated_at = timezone.now()
        institution.save()

        # Log audit event
        AuditService.log_institution_validated(
            admin_user=admin_user,
            institution_id=institution.id,
            institution_name=institution.name,
            request=request
        )

        # Send welcome email
        EmailService.send_welcome_email(
            user_email=institution.email,
            recipient_name=institution.name,
            institution_name=institution.name
        )

        logger.info(f"Institution {institution.id} validated by {admin_user.username}.")

    @classmethod
    @transaction.atomic
    def suspend_institution(cls, institution: Institution, admin_user: User, reason: str, request: HttpRequest):
        """
        Suspend une institution active.

        Args:
            institution (Institution): L'institution à suspendre.
            admin_user (User): L'administrateur qui effectue la suspension.
            reason (str): La raison de la suspension.
            request (HttpRequest): The Django request object.
        """
        if institution.status != Institution.Status.ACTIVE:
            logger.warning(f"Attempted to suspend an institution that is not active: {institution.id}")
            return

        institution.status = Institution.Status.SUSPENDED
        institution.save()

        # Log audit event
        AuditService.log_institution_suspended(
            admin_user=admin_user,
            institution_id=institution.id,
            institution_name=institution.name,
            reason=reason,
            request=request
        )

        logger.info(f"Institution {institution.id} suspended by {admin_user.username}.")

    @classmethod
    def get_institution_stats(cls, institution: Institution) -> Dict[str, Any]:
        """
        Récupère des statistiques de base pour une institution.

        Args:
            institution (Institution): L'institution pour laquelle récupérer les stats.

        Returns:
            Dict[str, Any]: Un dictionnaire de statistiques.
        """
        user_count = InstitutionUser.objects.filter(institution=institution).count()
        return {
            'user_count': user_count,
        }

    @classmethod
    @transaction.atomic
    def invite_user(cls, institution: Institution, email: str, role: InstitutionUser.Role, invited_by: User, request: HttpRequest) -> InstitutionUser:
        """
        Invite un nouvel utilisateur dans une institution.

        Args:
            institution (Institution): L'institution dans laquelle inviter l'utilisateur.
            email (str): L'e-mail de l'utilisateur à inviter.
            role (InstitutionUser.Role): Le rôle de l'utilisateur dans l'institution.
            invited_by (User): L'utilisateur qui envoie l'invitation.
            request (HttpRequest): The Django request object.

        Returns:
            InstitutionUser: Le lien InstitutionUser créé.
        """
        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                'username': email,
                'status': User.Status.PENDING,
            }
        )

        institution_user = InstitutionUser.objects.create(
            institution=institution,
            user=user,
            role=role,
            invited_by=invited_by,
        )

        # Generate a signed token for the user's ID
        token = signing.dumps(str(user.id), salt='user-verification')

        # Build the verification URL
        verification_path = reverse('verify_account', kwargs={'token': token})
        verification_url = request.build_absolute_uri(verification_path)

        EmailService.send_verification_email(
            user=user,
            verification_url=verification_url
        )

        logger.info(f"User {email} invited to institution {institution.name} with role {role} by {invited_by.username}.")
        return institution_user
