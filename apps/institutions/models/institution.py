from django.db import models
from apps.core.models import User
import uuid

class Institution(models.Model):
    """Entité émettrice de documents"""

    class Type(models.TextChoices):
        PUBLIC = 'PUBLIC', 'Institution Publique'
        PRIVATE = 'PRIVATE', 'Institution Privée'
        INTERNATIONAL = 'INTERNATIONAL', 'Organisation Internationale'
        UNIVERSITY = 'UNIVERSITY', 'Université'
        GOVERNMENT = 'GOVERNMENT', 'Gouvernement'

    class Status(models.TextChoices):
        PENDING = 'PENDING', 'En attente de validation'
        ACTIVE = 'ACTIVE', 'Active'
        SUSPENDED = 'SUSPENDED', 'Suspendue'
        REVOKED = 'REVOKED', 'Révoquée'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Informations de base
    name = models.CharField(max_length=255)  # Nom affiché
    legal_name = models.CharField(max_length=255)  # Nom légal
    slug = models.SlugField(unique=True)
    type = models.CharField(max_length=20, choices=Type.choices)

    # Contact
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    website = models.URLField(blank=True)

    # Adresse
    address_line1 = models.CharField(max_length=255)
    address_line2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country_code = models.CharField(max_length=2)  # ISO 3166-1 alpha-2

    # Identification légale
    registration_number = models.CharField(max_length=100, blank=True)
    tax_id = models.CharField(max_length=100, blank=True)

    # Statut et validation
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    validated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='validated_institutions'
    )
    validated_at = models.DateTimeField(null=True, blank=True)

    # Métadonnées
    logo = models.ImageField(upload_to='institutions/logos/', blank=True, null=True)
    description = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'institutions'
        db_table = 'institutions'
        ordering = ['name']
        indexes = [
            models.Index(fields=['status', 'type']),
            models.Index(fields=['country_code']),
            models.Index(fields=['slug']),
        ]

    def __str__(self):
        return self.name
