from django.db import models
from apps.core.models import User
from .institution import Institution
import uuid

class InstitutionUser(models.Model):
    """Liaison entre utilisateurs et institutions avec rôles"""

    class Role(models.TextChoices):
        ADMIN = 'ADMIN', 'Administrateur'
        SIGNER = 'SIGNER', 'Signataire'
        AUDITOR = 'AUDITOR', 'Auditeur'
        VIEWER = 'VIEWER', 'Lecteur'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=Role.choices)
    is_active = models.BooleanField(default=True)
    invited_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='invited_users'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'institutions'
        db_table = 'institution_users'
        unique_together = ['institution', 'user']
        indexes = [
            models.Index(fields=['institution', 'role']),
        ]
