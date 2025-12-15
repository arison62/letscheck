import uuid
from django.db import models
from apps.institutions.models import Institution
from apps.cryptography.models import CryptographicKey

class SignedDocument(models.Model):
    class DocumentStatus(models.TextChoices):
        AUTHENTIC = 'AUTHENTIC', 'Authentic'
        REVOKED = 'REVOKED', 'Revoked'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    institution = models.ForeignKey(Institution, on_delete=models.PROTECT, related_name='signed_documents')
    key = models.ForeignKey(CryptographicKey, on_delete=models.PROTECT, related_name='signed_documents')
    document_hash = models.CharField(max_length=64, unique=True, db_index=True)
    signature = models.TextField()
    status = models.CharField(max_length=50, choices=DocumentStatus.choices, default=DocumentStatus.AUTHENTIC)
    signed_at = models.DateTimeField(auto_now_add=True)
    revoked_at = models.DateTimeField(null=True, blank=True)
    revocation_reason = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f"Signed Document {self.document_hash[:10]}... by {self.institution.name}"
