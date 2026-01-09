# apps/core/models.py

from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid

class User(AbstractUser):
    """Utilisateur étendu avec rôles et statuts"""

    class Role(models.TextChoices):
        ADMIN = 'ADMIN', 'Administrateur Système'
        INSTITUTION = 'INSTITUTION', 'Utilisateur Institution'
        PUBLIC = 'PUBLIC', 'Utilisateur Public'

    class Status(models.TextChoices):
        PENDING = 'PENDING', 'En attente de validation'
        ACTIVE = 'ACTIVE', 'Actif'
        SUSPENDED = 'SUSPENDED', 'Suspendu'
        REVOKED = 'REVOKED', 'Révoqué'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.PUBLIC)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    phone = models.CharField(max_length=20, blank=True, null=True)
    email_verified = models.BooleanField(default=False)
    two_factor_enabled = models.BooleanField(default=False)
    last_login_ip = models.GenericIPAddressField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'core_users'
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['status', 'role']),
        ]


class AuditLog(models.Model):
    """Journal d'audit immuable de toutes les actions"""

    class ActionType(models.TextChoices):
        # Authentification
        LOGIN = 'LOGIN', 'Connexion'
        LOGOUT = 'LOGOUT', 'Déconnexion'
        LOGIN_FAILED = 'LOGIN_FAILED', 'Échec connexion'

        # Documents
        SIGN = 'SIGN', 'Signature document'
        VERIFY = 'VERIFY', 'Vérification document'
        REVOKE = 'REVOKE', 'Révocation document'

        # Clés
        KEY_CREATED = 'KEY_CREATED', 'Création clé'
        KEY_ROTATED = 'KEY_ROTATED', 'Rotation clé'
        KEY_REVOKED = 'KEY_REVOKED', 'Révocation clé'

        # Administration
        INSTITUTION_VALIDATED = 'INSTITUTION_VALIDATED', 'Institution validée'
        INSTITUTION_SUSPENDED = 'INSTITUTION_SUSPENDED', 'Institution suspendue'
        USER_UPD = 'USER_UPD', 'Utilisateur modifié'

    class ResourceType(models.TextChoices):
        USER = 'USER', 'Utilisateur'
        INSTITUTION = 'INSTITUTION', 'Institution'
        DOCUMENT = 'DOCUMENT', 'Document'
        KEY = 'KEY', 'Clé cryptographique'
        SYSTEM = 'SYSTEM', 'Système'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    action_type = models.CharField(max_length=50, choices=ActionType.choices)
    resource_type = models.CharField(max_length=20, choices=ResourceType.choices)
    resource_id = models.UUIDField(null=True, blank=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    success = models.BooleanField(default=True)
    details = models.JSONField(default=dict, blank=True)  # Données supplémentaires
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'core_audit_logs'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['action_type', 'timestamp']),
            models.Index(fields=['resource_type', 'resource_id']),
        ]

    def __str__(self):
        return f"{self.action_type} by {self.user} at {self.timestamp}"


class EmailTemplate(models.Model):
    """
    Modèle pour stocker les templates d'email multilingues.
    Permet de gérer facilement les sujets et corps des emails en version texte et HTML.
    """
    class TemplateType(models.TextChoices):
        WELCOME = 'WELCOME', 'E-mail de bienvenue'
        PASSWORD_RESET = 'PASSWORD_RESET', 'Réinitialisation de mot de passe'
        EMAIL_VERIFICATION = 'EMAIL_VERIFICATION', 'Vérification d\'e-mail'
        DOCUMENT_REVOKED = 'DOCUMENT_REVOKED', 'Document révoqué'
        KEY_EXPIRING = 'KEY_EXPIRING', 'Clé expirant bientôt'

    class Language(models.TextChoices):
        FRENCH = 'fr', 'Français'
        ENGLISH = 'en', 'English'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True, help_text="Nom interne unique pour le template (ex: 'welcome_email_fr')")
    template_type = models.CharField(max_length=50, choices=TemplateType.choices, help_text="Type de template utilisé pour le déclenchement.")
    subject = models.CharField(max_length=255, help_text="Sujet de l'e-mail.")
    body_text = models.TextField(blank=True, help_text="Corps de l'e-mail en format texte brut.")
    body_html = models.TextField(help_text="Corps de l'e-mail en format HTML.")
    language = models.CharField(max_length=5, choices=Language.choices, default=Language.FRENCH)
    active = models.BooleanField(default=True, help_text="Désactiver pour ne plus utiliser ce template.")

    class Meta:
        db_table = 'core_email_templates'
        unique_together = ('template_type', 'language')
        ordering = ['name']
        indexes = [
            models.Index(fields=['template_type', 'language']),
        ]

    def __str__(self):
        return f"{self.get_template_type_display()} ({self.get_language_display()})"
