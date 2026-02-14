import uuid
from django.db import models
from django.utils.text import slugify

class Institution(models.Model):
    class InstitutionType(models.TextChoices):
        PUBLIC = 'PUBLIC', 'Public'
        PRIVATE = 'PRIVATE', 'Private'
        UNIVERSITY = 'UNIVERSITY', 'University'
        GOVERNMENT = 'GOVERNMENT', 'Government'
        INTERNATIONAL = 'INTERNATIONAL', 'International'

    class InstitutionStatus(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        ACTIVE = 'ACTIVE', 'Active'
        SUSPENDED = 'SUSPENDED', 'Suspended'
        REVOKED = 'REVOKED', 'Revoked'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    logo = models.ImageField(upload_to='institution_logos/', null=True, blank=True)
    country_code = models.CharField(max_length=2)
    type = models.CharField(max_length=50, choices=InstitutionType.choices, default=InstitutionType.PUBLIC)
    status = models.CharField(max_length=50, choices=InstitutionStatus.choices, default=InstitutionStatus.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    @property
    def logo_url(self):
        if self.logo and hasattr(self.logo, 'url'):
            return self.logo.url
        return None
