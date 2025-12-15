import uuid
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

class User(AbstractUser):
    """
    Modèle utilisateur personnalisé où l'email est l'identifiant unique pour l'authentification.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = None  # On n'utilise pas de nom d'utilisateur
    email = models.EmailField(_('email address'), unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    def __str__(self):
        return self.email

# I'll keep the AuditLog model here as it's part of the core app
class AuditLog(models.Model):
    class ActionType(models.TextChoices):
        CREATE = 'CREATE', 'Create'
        UPDATE = 'UPDATE', 'Update'
        DELETE = 'DELETE', 'Delete'
        VERIFY = 'VERIFY', 'Verify'
        LOGIN = 'LOGIN', 'Login'
        LOGOUT = 'LOGOUT', 'Logout'

    class ResourceType(models.TextChoices):
        DOCUMENT = 'DOCUMENT', 'Document'
        INSTITUTION = 'INSTITUTION', 'Institution'
        USER = 'USER', 'User'
        KEY = 'KEY', 'Key'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )
    action_type = models.CharField(max_length=50, choices=ActionType.choices)
    resource_type = models.CharField(max_length=50, choices=ResourceType.choices)
    resource_id = models.CharField(max_length=255, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=255, null=True, blank=True)
    details = models.TextField(null=True, blank=True)
    success = models.BooleanField(default=True)

    def __str__(self):
        user_email = self.user.email if self.user else "Anonymous"
        return f"{self.action_type} on {self.resource_type} by {user_email} at {self.timestamp}"
