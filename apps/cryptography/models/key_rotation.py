from django.db import models
from apps.core.models import User
from .cryptographic_key import CryptographicKey
import uuid

class KeyRotation(models.Model):
    """Historique des rotations de clés"""

    class RotationType(models.TextChoices):
        SCHEDULED = 'SCHEDULED', 'Rotation planifiée'
        MANUAL = 'MANUAL', 'Rotation manuelle'
        SECURITY = 'SECURITY', 'Rotation de sécurité'
        COMPROMISED = 'COMPROMISED', 'Clé compromise'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    old_key = models.ForeignKey(
        CryptographicKey,
        on_delete=models.CASCADE,
        related_name='rotations_from'
    )
    new_key = models.ForeignKey(
        CryptographicKey,
        on_delete=models.CASCADE,
        related_name='rotations_to'
    )
    rotation_type = models.CharField(max_length=20, choices=RotationType.choices)
    reason = models.TextField()
    performed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'cryptography'
        db_table = 'key_rotations'
        ordering = ['-timestamp']
