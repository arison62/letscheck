from django.db import models
from apps.institutions.models import Institution
from apps.core.models import User
import uuid

class CryptographicKey(models.Model):
    """Métadonnées des clés publiques (JAMAIS les clés privées)"""

    class Algorithm(models.TextChoices):
        RSA_2048 = 'RSA_2048', 'RSA 2048 bits'
        RSA_4096 = 'RSA_4096', 'RSA 4096 bits (recommandé)'
        ECDSA_P256 = 'ECDSA_P256', 'ECDSA P-256'
        ECDSA_P384 = 'ECDSA_P384', 'ECDSA P-384 (recommandé)'

    class Status(models.TextChoices):
        ACTIVE = 'ACTIVE', 'Active'
        EXPIRING_SOON = 'EXPIRING_SOON', 'Expire bientôt'
        EXPIRED = 'EXPIRED', 'Expirée'
        REVOKED = 'REVOKED', 'Révoquée'
        ROTATED = 'ROTATED', 'Remplacée par rotation'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE, related_name='keys')

    # Clé publique uniquement (format PEM)
    public_key = models.TextField()
    fingerprint = models.CharField(max_length=128, unique=True)  # Hash de la clé publique

    # Algorithme et paramètres
    algorithm = models.CharField(max_length=20, choices=Algorithm.choices)
    key_size = models.IntegerField()  # En bits

    # Statut et validité
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    revoked_at = models.DateTimeField(null=True, blank=True)
    revocation_reason = models.TextField(blank=True)

    # Rotation (clé parente si rotation)
    parent_key = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='rotated_keys'
    )

    # Validation
    validated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='validated_keys'
    )
    validated_at = models.DateTimeField(null=True, blank=True)

    # Métadonnées
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        app_label = 'cryptography'
        db_table = 'cryptographic_keys'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['institution', 'status']),
            models.Index(fields=['fingerprint']),
            models.Index(fields=['expires_at']),
        ]

    def __str__(self):
        return f"{self.institution.name} - {self.algorithm} - {self.fingerprint[:16]}"
