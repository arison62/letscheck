import uuid
from django.db import models
from apps.institutions.models import Institution

class CryptographicKey(models.Model):
    class KeyStatus(models.TextChoices):
        ACTIVE = 'ACTIVE', 'Active'
        EXPIRED = 'EXPIRED', 'Expired'
        REVOKED = 'REVOKED', 'Revoked'

    class KeyAlgorithm(models.TextChoices):
        RSA = 'RSA', 'RSA'
        # ECDSA = 'ECDSA', 'ECDSA' # Future support

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE, related_name='keys')
    public_key = models.TextField()
    algorithm = models.CharField(max_length=50, choices=KeyAlgorithm.choices, default=KeyAlgorithm.RSA)
    status = models.CharField(max_length=50, choices=KeyStatus.choices, default=KeyStatus.ACTIVE)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Key for {self.institution.name} ({self.get_status_display()})"
