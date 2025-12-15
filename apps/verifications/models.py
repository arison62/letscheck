import uuid
from django.db import models
from apps.documents.models import SignedDocument

class SuspiciousReport(models.Model):
    class ReportType(models.TextChoices):
        FAKE = 'FAKE', 'Fake Document'
        ALTERED = 'ALTERED', 'Altered Document'
        UNAUTHORIZED = 'UNAUTHORIZED', 'Unauthorized Signature'
        OTHER = 'OTHER', 'Other'

    class ReportStatus(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        INVESTIGATING = 'INVESTIGATING', 'Investigating'
        RESOLVED = 'RESOLVED', 'Resolved'
        DISMISSED = 'DISMISSED', 'Dismissed'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    document = models.ForeignKey(SignedDocument, on_delete=models.SET_NULL, null=True, blank=True, related_name='reports')
    document_hash = models.CharField(max_length=64, db_index=True)
    report_type = models.CharField(max_length=50, choices=ReportType.choices)
    reason = models.TextField()
    status = models.CharField(max_length=50, choices=ReportStatus.choices, default=ReportStatus.PENDING)
    reporter_email = models.EmailField(null=True, blank=True)
    reporter_name = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Report for {self.document_hash[:10]}... ({self.get_status_display()})"
