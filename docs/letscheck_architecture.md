# Architecture Complète - Application Let's Check

## 1. Vue d'Ensemble de l'Architecture

### 1.1 Principes Fondamentaux
- **Sécurité First**: Clés privées jamais exposées au serveur
- **Architecture Hybride**: Backend centralisé + génération locale des clés
- **Modularité**: Apps Django indépendantes et réutilisables
- **Performance**: <3s pour vérification, support 1M vérifications/jour
- **Conformité**: RGPD, standards cryptographiques (RSA-4096/ECDSA P-384)

### 1.2 Stack Technologique

**Backend:**
- Django 5.x + Django Ninja
- Inertia.js pour intégration React
- PostgreSQL 15+ (base de données principale)
- Redis (cache et sessions optionnel)
- Huey (tâches asynchrones)
- Nginx + Gunicorn (production)

**Frontend Publique:**
- React 18+
- Inertia.js (pont avec Django)
- Tailwind CSS + Shadcn UI
- Zustand (gestion état)
- Crypto.js (hashing côté client)

**Application Desktop:**
- Flet/Python (cross-platform)
- Cryptography library
- Keyring (stockage sécurisé clés)
- Requests (communication API)

**Infrastructure:**
- Docker + Docker Compose
- GitHub Actions (CI/CD)
- AWS/DigitalOcean (hébergement)

### 1.3 Schéma d'Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    UTILISATEURS FINAUX                       │
├──────────────┬────────────────┬─────────────────────────────┤
│   Public     │  Institutions  │      Administrateurs        │
│   (Web)      │   (Desktop)    │        (Web Admin)          │
└──────┬───────┴────────┬───────┴──────────────┬──────────────┘
       │                │                       │
       ▼                ▼                       ▼
┌──────────────────────────────────────────────────────────────┐
│               COUCHE PRÉSENTATION                             │
├──────────────────────┬───────────────────────────────────────┤
│  React Public (SPA)  │  Flet Desktop App  │  Django Admin   │
│   + Inertia.js       │   (Python)         │   + React       │
└──────────┬───────────┴─────────┬──────────┴─────────┬────────┘
           │                     │                     │
           └─────────────────────┼─────────────────────┘
                                 │ HTTPS/WSS
                    ┌────────────▼────────────┐
                    │    API GATEWAY          │
                    │  (Rate Limiting, Auth)  │
                    └────────────┬────────────┘
                                 │
           ┌─────────────────────┼─────────────────────┐
           │                     │                     │
           ▼                     ▼                     ▼
┌──────────────────────────────────────────────────────────────┐
│                 COUCHE APPLICATION (Django)                   │
├──────────┬──────────┬──────────┬──────────┬──────────────────┤
│   core   │ institu- │  crypto- │documents │ verifications    │
│  (auth,  │  tions   │  graphy  │ (signing)│  (checking)      │
│  audit)  │          │  (keys)  │          │                  │
└────┬─────┴────┬─────┴────┬─────┴────┬─────┴────┬─────────────┘
     │          │          │          │          │
     └──────────┴──────────┴──────────┴──────────┘
                         │
           ┌─────────────┼─────────────┐
           │             │             │
           ▼             ▼             ▼
     ┌─────────┐   ┌──────────┐  ┌─────────┐
     │PostgreSQL│   │  Redis   │  │ Huey    │
     │  (BDD)   │   │ (Cache)  │  │ (Jobs)  │
     └──────────┘   └──────────┘  └─────────┘
```

### 1.4 Flux de Données Principaux

**Flux 1: Signature de Document (Institution)**
```
Desktop App → Génération clé locale (privée/publique)
           → Signature document local (avec clé privée)
           → Hash + Métadonnées (sans clé privée)
           → API Backend → PostgreSQL
           → Réponse: ID document + QR code
```

**Flux 2: Vérification de Document (Public)**
```
Web Interface → Upload/Scan document
              → Hash calculé côté client
              → API Backend → Validation hash/signature
              → PostgreSQL (recherche métadonnées)
              → Réponse: Authentique/Invalide + Certificat
```

**Flux 3: Audit et Administration**
```
Toute action → AuditLog enregistré
            → Dashboard Admin → Visualisation
            → Rapports exportables (CSV/PDF)
```

---

## 2. Modèles de Données par Module Django

### Structure des Apps Django
```bash
letscheck_project/
├── manage.py
├── config/                    # Settings Django
│   ├── settings/
│   │   ├── base.py
│   │   ├── development.py
│   │   ├── production.py
│   └── urls.py
├── apps/
│   ├── core/                  # App fondamentale
│   ├── institutions/          # Gestion institutions
│   ├── cryptography/          # Clés et algorithmes
│   ├── documents/             # Documents signés
│   ├── verifications/         # Vérifications publiques
│   └── analytics/             # Statistiques
├── requirements.txt
└── frontend/                  # Frontend ReactTs + Inertia.js


```

### 2.1 App: `core` (Fondation)

**Responsabilité**: Authentification, audit, emails, utilitaires communs

```python
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
        INSTITUTION_VALIDATED = 'INST_VALID', 'Institution validée'
        INSTITUTION_SUSPENDED = 'INST_SUSP', 'Institution suspendue'
        USER_UPDATED = 'USER_UPD', 'Utilisateur modifié'
    
    class ResourceType(models.TextChoices):
        USER = 'USER', 'Utilisateur'
        INSTITUTION = 'INSTITUTION', 'Institution'
        DOCUMENT = 'DOCUMENT', 'Document'
        KEY = 'KEY', 'Clé cryptographique'
        SYSTEM = 'SYSTEM', 'Système'
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    action_type = models.CharField(max_length=20, choices=ActionType.choices)
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


### 2.2 App: `institutions` (Gestion Institutions)

**Responsabilité**: Entités émettrices, validation, hiérarchie

```python
# apps/institutions/models.py

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
        db_table = 'institutions'
        ordering = ['name']
        indexes = [
            models.Index(fields=['status', 'type']),
            models.Index(fields=['country_code']),
            models.Index(fields=['slug']),
        ]
    
    def __str__(self):
        return self.name


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
        db_table = 'institution_users'
        unique_together = ['institution', 'user']
        indexes = [
            models.Index(fields=['institution', 'role']),
        ]
```

---

### 2.3 App: `cryptography` (Clés et Signatures)

**Responsabilité**: Métadonnées des clés, rotation, algorithmes

```python
# apps/cryptography/models.py

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
        db_table = 'cryptographic_keys'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['institution', 'status']),
            models.Index(fields=['fingerprint']),
            models.Index(fields=['expires_at']),
        ]
    
    def __str__(self):
        return f"{self.institution.name} - {self.algorithm} - {self.fingerprint[:16]}"


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
        db_table = 'key_rotations'
        ordering = ['-timestamp']
```

---

### 2.4 App: `documents` (Documents Signés)

**Responsabilité**: Documents émis, signatures, révocations

```python
# apps/documents/models.py

from django.db import models
from apps.institutions.models import Institution
from apps.cryptography.models import CryptographicKey
from apps.core.models import User
import uuid

class SignedDocument(models.Model):
    """Document signé avec métadonnées"""
    
    class FileType(models.TextChoices):
        PDF = 'PDF', 'PDF'
        JPEG = 'JPEG', 'JPEG/JPG'
        PNG = 'PNG', 'PNG'
        DOCX = 'DOCX', 'DOCX'
        XML = 'XML', 'XML'
    
    class Status(models.TextChoices):
        ACTIVE = 'ACTIVE', 'Valide'
        REVOKED = 'REVOKED', 'Révoqué'
        EXPIRED = 'EXPIRED', 'Expiré'
        SUSPENDED = 'SUSPENDED', 'Suspendu'
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE, related_name='documents')
    key = models.ForeignKey(CryptographicKey, on_delete=models.PROTECT, related_name='signed_documents')
    
    # Identifiants du document
    document_hash = models.CharField(max_length=128, unique=True, db_index=True)  # SHA-256
    signature = models.TextField()  # Signature numérique (base64)
    
    # Type et métadonnées
    file_type = models.CharField(max_length=10, choices=FileType.choices)
    original_filename = models.CharField(max_length=255, blank=True)
    file_size = models.BigIntegerField(null=True, blank=True)  # En octets
    
    # QR Code et stéganographie
    qr_code_data = models.TextField(blank=True)  # Données encodées dans QR
    has_steganography = models.BooleanField(default=False)
    steganography_method = models.CharField(max_length=50, blank=True)  # DCT, LSB, etc.
    
    # Statut
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)
    
    # Dates
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    revoked_at = models.DateTimeField(null=True, blank=True)
    revoked_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='revoked_documents'
    )
    revocation_reason = models.TextField(blank=True)
    
    # Métadonnées additionnelles
    metadata = models.JSONField(default=dict, blank=True)  # Données contextuelles
    
    # URL externe (optionnel, si document stocké ailleurs)
    external_url = models.URLField(blank=True)
    
    class Meta:
        db_table = 'signed_documents'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['document_hash']),
            models.Index(fields=['institution', 'status']),
            models.Index(fields=['created_at']),
            models.Index(fields=['status', 'expires_at']),
        ]
    
    def __str__(self):
        return f"{self.institution.name} - {self.document_hash[:16]}"


class DocumentVerification(models.Model):
    """Enregistrement de chaque vérification de document"""
    
    class Method(models.TextChoices):
        UPLOAD = 'UPLOAD', 'Upload fichier'
        QR_SCAN = 'QR_SCAN', 'Scan QR code'
        HASH_INPUT = 'HASH_INPUT', 'Saisie hash manuel'
        STEGANOGRAPHY = 'STEGANOGRAPHY', 'Extraction stéganographique'
        API = 'API', 'Vérification API'
    
    class Result(models.TextChoices):
        AUTHENTIC = 'AUTHENTIC', 'Authentique'
        INVALID_SIGNATURE = 'INVALID_SIGNATURE', 'Signature invalide'
        NOT_FOUND = 'NOT_FOUND', 'Document non trouvé'
        REVOKED = 'REVOKED', 'Document révoqué'
        EXPIRED = 'EXPIRED', 'Document expiré'
        KEY_EXPIRED = 'KEY_EXPIRED', 'Clé expirée'
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    document = models.ForeignKey(
        SignedDocument,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='verifications'
    )
    
    # Hash fourni par le vérifieur (peut différer du hash stocké si invalide)
    provided_hash = models.CharField(max_length=128)
    
    # Informations vérifieur
    verifier_ip = models.GenericIPAddressField()
    verifier_user_agent = models.TextField(blank=True)
    verifier_country = models.CharField(max_length=2, blank=True)  # GeoIP
    
    # Méthode et résultat
    method = models.CharField(max_length=20, choices=Method.choices)
    result = models.CharField(max_length=30, choices=Result.choices)
    
    # Timing
    timestamp = models.DateTimeField(auto_now_add=True)
    verification_duration_ms = models.IntegerField(null=True)  # Durée en ms
    
    # Certificat généré (URL vers PDF)
    certificate_url = models.URLField(blank=True)
    
    # Métadonnées
    details = models.JSONField(default=dict, blank=True)
    
    class Meta:
        db_table = 'document_verifications'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['document', 'timestamp']),
            models.Index(fields=['provided_hash']),
            models.Index(fields=['verifier_ip', 'timestamp']),
            models.Index(fields=['result', 'timestamp']),
        ]
```

---

### 2.5 App: `verifications` (Vérifications Publiques)

**Responsabilité**: Requêtes publiques, signalements

```python
# apps/verifications/models.py

from django.db import models
from apps.documents.models import SignedDocument
import uuid

class VerificationRequest(models.Model):
    """Requête de vérification (traçabilité complète)"""
    
    class Status(models.TextChoices):
        SUCCESS = 'SUCCESS', 'Succès'
        FAILURE = 'FAILURE', 'Échec'
        ERROR = 'ERROR', 'Erreur système'
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Hash fourni
    document_hash = models.CharField(max_length=128, db_index=True)
    
    # Informations requête
    uploader_ip = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    referer = models.URLField(blank=True)
    
    # Résultat
    status = models.CharField(max_length=10, choices=Status.choices)
    matched_document = models.ForeignKey(
        SignedDocument,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    
    # Timing
    timestamp = models.DateTimeField(auto_now_add=True)
    processing_time_ms = models.IntegerField(null=True)
    
    # Détails additionnels
    details = models.JSONField(default=dict, blank=True)
    
    class Meta:
        db_table = 'verification_requests'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['document_hash', 'timestamp']),
            models.Index(fields=['uploader_ip', 'timestamp']),
        ]


class SuspiciousReport(models.Model):
    """Signalement de document suspect ou frauduleux"""
    
    class Status(models.TextChoices):
        PENDING = 'PENDING', 'En attente'
        UNDER_REVIEW = 'UNDER_REVIEW', 'En cours de révision'
        CONFIRMED = 'CONFIRMED', 'Confirmé frauduleux'
        REJECTED = 'REJECTED', 'Rejeté (non frauduleux)'
        CLOSED = 'CLOSED', 'Clos'
    
    class ReportType(models.TextChoices):
        FAKE_DOCUMENT = 'FAKE', 'Faux document'
        ALTERED = 'ALTERED', 'Document modifié'
        UNAUTHORIZED = 'UNAUTHORIZED', 'Utilisation non autorisée'
        OTHER = 'OTHER', 'Autre'
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    document = models.ForeignKey(
        SignedDocument,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='reports'
    )
    
    # Informations signalement
    document_hash = models.CharField(max_length=128)  # Au cas où document pas trouvé
    report_type = models.CharField(max_length=20, choices=ReportType.choices)
    reason = models.TextField()
    
    # Informations signaleur
    reporter_ip = models.GenericIPAddressField()
    reporter_email = models.EmailField(blank=True)  # Optionnel
    reporter_name = models.CharField(max_length=100, blank=True)  # Optionnel
    
    # Statut
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    reviewed_by = models.ForeignKey(
        'core.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    admin_notes = models.TextField(blank=True)
    
    # Dates
    timestamp = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Métadonnées
    evidence_urls = models.JSONField(default=list, blank=True)  # Screenshots, etc.
    metadata = models.JSONField(default=dict, blank=True)
    
    class Meta:
        db_table = 'suspicious_reports'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['status', 'timestamp']),
            models.Index(fields=['document', 'status']),
        ]
```

---

### 2.6 App: `analytics` (Statistiques)

**Responsabilité**: Agrégation de données, rapports

```python
# apps/analytics/models.py

from django.db import models
from django.contrib.postgres.fields import DateRangeField
from apps.institutions.models import Institution
import uuid

class Statistic(models.Model):
    """Agrégation de métriques pour tableaux de bord"""
    
    class MetricType(models.TextChoices):
        VERIFICATIONS_TOTAL = 'VERIF_TOTAL', 'Vérifications totales'
        VERIFICATIONS_SUCCESS = 'VERIF_SUCCESS', 'Vérifications réussies'
        VERIFICATIONS_FAILED = 'VERIF_FAILED', 'Vérifications échouées'
        DOCUMENTS_SIGNED = 'DOC_SIGNED', 'Documents signés'
        DOCUMENTS_REVOKED = 'DOC_REVOKED', 'Documents révoqués'
        KEYS_CREATED = 'KEY_CREATED', 'Clés créées'
        KEYS_ROTATED = 'KEY_ROTATED', 'Clés pivotées'
        REPORTS_RECEIVED = 'REPORTS', 'Signalements reçus'
        INSTITUTIONS_ACTIVE = 'INST_ACTIVE', 'Institutions actives'
    
    class Period(models.TextChoices):
        HOURLY = 'HOURLY', 'Horaire'
        DAILY = 'DAILY', 'Journalier'
        WEEKLY = 'WEEKLY', 'Hebdomadaire'
        MONTHLY = 'MONTHLY', 'Mensuel'
        YEARLY = 'YEARLY', 'Annuel'
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Scope (global ou par institution)
    institution = models.ForeignKey(
        Institution,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='statistics'
    )
    
    # Métrique
    metric_type = models.CharField(max_length=20, choices=MetricType.choices)
    value = models.BigIntegerField()
    
    # Période
    period_type = models.CharField(max_length=10, choices=Period.choices)
    period_start = models.DateTimeField()
    period_end = models.DateTimeField()
    
    # Métadonnées
    breakdown = models.JSONField(default=dict, blank=True)  # Détails supplémentaires
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'analytics_statistics'
        unique_together = ['institution', 'metric_type', 'period_type', 'period_start']
        indexes = [
            models.Index(fields=['metric_type', 'period_start']),
            models.Index(fields=['institution', 'metric_type']),
        ]


class PerformanceMetric(models.Model):
    """Métriques de performance système"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # API endpoints
    endpoint = models.CharField(max_length=255)
    method = models.CharField(max_length=10)  # GET, POST, etc.
    
    # Performance
    avg_response_time_ms = models.FloatField()
    p95_response_time_ms = models.FloatField()
    p99_response_time_ms = models.FloatField()
    
    # Volume
    request_count = models.BigIntegerField()
    error_count = models.BigIntegerField()
    
    # Période
    timestamp = models.DateTimeField()
    
    class Meta:
        db_table = 'analytics_performance'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['endpoint', 'timestamp']),
        ]
```

---

## 3. Description Détaillée des Interfaces

### 3.1 Interface Publique de Vérification (Web React)

#### Objectif
Permettre au grand public de vérifier l'authenticité de documents de manière simple, rapide (<5s) et gratuite, sans inscription.

#### Pages et Composants

##### 3.1.1 Page d'Accueil (`/`)
**Objectif**: Présenter Let's Check et rediriger vers la vérification

**Éléments UI**:
- **Header**:
  - Logo Let's Check
  - Menu de navigation: Accueil | Vérifier | FAQ | Contact
  - Sélecteur de langue (FR/EN)
  
- **Hero Section**:
  - Titre: "Vérifiez l'authenticité de vos documents en quelques secondes"
  - Sous-titre: "Service gratuit, sécurisé et instantané pour valider diplômes, certificats et documents officiels"
  - CTA principal: Bouton "Vérifier un Document" (taille XL, couleur accent)
  - Illustration: Animation SVG montrant un document avec un checkmark
  
- **Section Fonctionnalités** (3 colonnes):
  1. **Rapide**: Icône chrono + "Vérification en moins de 5 secondes"
  2. **Sécurisé**: Icône cadenas + "Cryptographie de niveau bancaire"
  3. **Gratuit**: Icône gratuit + "Service accessible à tous sans frais"
  
- **Section Comment ça marche** (Timeline visuelle):
  1. "Uploadez votre document ou scannez le QR code"
  2. "Notre système vérifie la signature cryptographique"
  3. "Recevez instantanément le résultat avec certificat"
  
- **Section Statistiques** (compteurs animés):
  - Documents vérifiés aujourd'hui
  - Institutions partenaires
  - Taux de satisfaction

- **Footer**:
  - Liens: Mentions légales | Politique de confidentialité | CGU
  - Réseaux sociaux
  - © Let's Check 2024

**Interactions**:
- Hover sur CTA: effet de scale + ombre
- Scroll smooth vers sections
- Compteurs animés au scroll

**Composants Shadcn UI**:
- Button (variant="default", size="lg")
- Card pour fonctionnalités
- Badge pour statistiques

---

##### 3.1.2 Page de Vérification (`/verify`)
**Objectif**: Interface centrale de vérification multi-méthodes

**Layout**:
- Breadcrumb: Accueil > Vérifier
- Titre centré: "Vérifier l'authenticité d'un document"
- Zone de vérification (Card centrale, max-width: 800px)

**Zone de Vérification (Tabs)**:

**Tab 1: Upload Fichier** (par défaut)
- Zone drag-and-drop stylisée:
  - Icône upload + "Glissez votre document ici ou cliquez pour parcourir"
  - Formats acceptés affichés: PDF, JPG, PNG, DOCX (max 10MB)
  - Progression bar lors de l'upload
- Bouton "Vérifier" (désactivé jusqu'à upload complet)

**Tab 2: Scanner QR Code**
- Activation webcam avec permission explicite
- Prévisualisation caméra en temps réel
- Overlay avec guides pour cadrage QR
- Détection automatique + vibration/son sur détection
- Bouton "Autoriser la caméra" si non activée

**Tab 3: Entrer Hash Manuel**
- Input texte large avec validation format (64 caractères hex pour SHA-256)
- Aide contextuelle: "Le hash se trouve généralement au bas du document"
- Bouton "Vérifier"

**Résultat de Vérification** (s'affiche en dessous après soumission):

**Cas 1: Document Authentique** (fond vert clair)
- Icône: Grand checkmark animé (Lucide Check)
- Titre: "✓ Document Authentique"
- Informations:
  - Institution émettrice (nom + logo)
  - Date de signature
  - Type de document
  - Algorithme de signature
  - Statut: "Valide" (badge vert)
- Actions:
  - Bouton "Télécharger le Certificat de Vérification" (PDF généré)
  - Bouton "Voir l'historique de vérification"
  - Bouton "Signaler un problème" (secondaire)

**Cas 2: Document Invalide** (fond rouge clair)
- Icône: X rouge animé (Lucide X)
- Titre: "✗ Document Invalide"
- Raison détaillée:
  - "Signature numérique invalide"
  - "Document modifié après signature"
  - "Clé de signature révoquée"
  - Etc.
- Message: "Ce document ne peut pas être authentifié. Il peut avoir été modifié ou falsifié."
- Actions:
  - Bouton "Signaler comme Document Frauduleux" (alerte)
  - Lien "En savoir plus sur la sécurité"

**Cas 3: Document Non Trouvé** (fond orange clair)
- Icône: Question mark (Lucide HelpCircle)
- Titre: "⚠ Document Non Trouvé"
- Message: "Ce document n'est pas enregistré dans notre base de données."
- Explications:
  - "L'institution émettrice n'utilise pas Let's Check"
  - "Le document est peut-être ancien (pré-2024)"
- Actions:
  - Bouton "Contacter l'institution émettrice"
  - Bouton "Signaler comme Suspect"

**Cas 4: Document Révoqué** (fond rouge foncé)
- Icône: Ban (Lucide Ban)
- Titre: "🚫 Document Révoqué"
- Message critique: "Ce document a été officiellement révoqué par l'institution émettrice."
- Détails:
  - Date de révocation
  - Raison (si publique)
- Avertissement: "N'acceptez PAS ce document comme valide."

**Historique des Vérifications** (accordion en dessous):
- Tableau:
  - Date/heure
  - Méthode (upload/QR/hash)
  - IP (tronquée pour confidentialité)
  - Résultat
- Pagination si > 10 entrées

**Interactions**:
- Upload: Spinner pendant calcul hash côté client (Web Crypto API)
- Résultat: Animation d'apparition (slide-in)
- Feedback haptique sur mobile (si disponible)
- Copie hash: bouton avec toast de confirmation

**Composants Shadcn UI**:
- Tabs pour méthodes de vérification
- Card pour résultats
- Alert (variant="success", "destructive", "warning")
- Progress pour upload
- Accordion pour historique
- Table pour affichage historique

**Accessibilité**:
- ARIA labels sur tous les inputs
- Focus management sur résultats
- Annonces screen reader pour résultats
- Clavier complet (Tab navigation)

---

##### 3.1.3 Modal de Signalement
**Déclenchement**: Bouton "Signaler" depuis page vérification

**Contenu**:
- Titre: "Signaler un Document Suspect"
- Form:
  - Radio buttons: Type de problème
    - Document falsifié
    - Document modifié
    - Utilisation non autorisée
    - Autre
  - Textarea: Description détaillée (500 caractères max)
  - Input email (optionnel): "Pour un suivi de votre signalement"
  - Checkbox: "J'accepte que mes informations soient partagées avec l'institution"
  - Upload: "Joindre une preuve (screenshot, etc.)" (optionnel)
- Buttons:
  - "Envoyer le Signalement" (primary)
  - "Annuler" (ghost)

**Validation**:
- Type obligatoire
- Description min 50 caractères
- Prévention spam: limite 3 signalements/IP/jour

**Après soumission**:
- Toast de confirmation: "Signalement enregistré. Référence: #XXXXX"
- Email de confirmation si fourni

---

##### 3.1.4 Page FAQ (`/faq`)
**Structure**: Accordion avec questions fréquentes

Catégories:
1. **Généralités**:
   - Qu'est-ce que Let's Check?
   - Comment fonctionne la vérification?
   - Est-ce gratuit?

2. **Sécurité**:
   - Mes documents sont-ils stockés?
   - Comment protégez-vous mes données?
   - Qu'est-ce qu'une signature numérique?

3. **Utilisation**:
   - Quels formats sont supportés?
   - Que faire si mon document n'est pas trouvé?
   - Comment signaler un faux document?

4. **Pour les Institutions**:
   - Comment rejoindre Let's Check?
   - Combien ça coûte?
   - Quel est le processus de validation?

**Composants**:
- Accordion (Shadcn UI)
- Search bar pour filtrer questions

---

### 3.2 Interface d'Administration (Django Admin + React)

#### Objectif
Tableau de bord complet pour administrateurs système: validation institutions, gestion des clés, audit, statistiques.

#### Architecture Technique
- Django Admin customisé avec templates Inertia
- Composants React intégrés via Inertia.js
- Authentication: Django sessions + permissions
- RBAC strict (seuls ADMIN users)

---

##### 3.2.1 Dashboard Administrateur (`/admin/dashboard`)
**Layout**: Sidebar + Contenu principal

**Sidebar** (navigation):
- Logo + "Admin Panel"
- Menu items (icons Lucide):
  - 📊 Tableau de Bord
  - 🏢 Institutions
  - 🔑 Clés Cryptographiques
  - 📄 Documents
  - 🚨 Signalements
  - 👥 Utilisateurs
  - 📈 Statistiques & Rapports
  - 📝 Logs d'Audit
  - ⚙️ Paramètres
- User dropdown (en bas): Profil | Déconnexion

**Contenu Principal - Tableau de Bord**:

**Section 1: Métriques Clés** (4 cards en ligne)
1. **Institutions Actives**: Chiffre + sparkline évolution 7 jours
2. **Vérifications Aujourd'hui**: Chiffre + % vs hier
3. **Signalements Pending**: Chiffre en rouge si > 10
4. **Clés Expirant <30 jours**: Alerte si > 0

**Section 2: Graphiques** (2 colonnes)
- **Gauche**: Chart.js Line - "Vérifications sur 30 jours"
  - Lignes: Succès (vert) | Échecs (rouge) | Total (bleu)
  - Filtres: 7j | 30j | 90j | 1an
- **Droite**: Chart.js Doughnut - "Répartition des résultats de vérification"
  - Segments: Authentique | Invalide | Non trouvé | Révoqué

**Section 3: Alertes & Actions Requises** (liste priorisée)
- Badge rouge: "15 institutions en attente de validation" → Lien "Valider"
- Badge orange: "8 signalements non traités" → Lien "Traiter"
- Badge jaune: "3 clés expirent dans 7 jours" → Lien "Notifier"

**Section 4: Activité Récente** (timeline)
- Liste chronologique des 20 dernières actions:
  - Icône + "Institution 'Université XYZ' validée par Admin1"
  - Icône + "Clé révoquée pour Institution 'ABC'"
  - Etc.
- Bouton "Voir tous les logs" → Page audit

**Composants**:
- Card pour métriques
- Chart.js pour graphiques
- Badge pour alertes
- Timeline custom React

---

##### 3.2.2 Gestion des Institutions (`/admin/institutions`)
**Objectif**: Valider, suspendre, révoquer les institutions

**Layout**: Tableau filtrable + actions bulk

**Filtres** (au-dessus du tableau):
- Dropdown: Statut (Tous | Pending | Active | Suspended | Revoked)
- Dropdown: Type (Tous | Public | Privée | Université | etc.)
- Search: Recherche par nom
- Date range: Date d'inscription

**Tableau** (colonnes):
1. Logo (thumbnail)
2. Nom institution (lien vers détail)
3. Type (badge coloré)
4. Pays (drapeau + code)
5. Statut (badge avec icône)
6. Date inscription
7. Nb documents signés
8. Actions (dropdown):
   - Voir détails
   - Valider (si PENDING)
   - Suspendre/Activer
   - Révoquer
   - Voir logs

**Actions Bulk** (checkbox multi-sélection):
- "Valider sélection" (si PENDING)
- "Suspendre sélection"
- "Exporter CSV"

**Pagination**: 25/50/100 items par page

**Modal Validation d'Institution**:
- Informations à vérifier:
  - Nom légal
  - Adresse complète
  - Numéro d'enregistrement
  - Documents justificatifs (liens uploadés par l'institution)
- Checklist admin:
  - ☐ Identité vérifiée
  - ☐ Documents légaux vérifiés
  - ☐ Contact validé
- Textarea: Notes internes
- Actions:
  - "Valider et Activer" (envoie email de bienvenue)
  - "Rejeter" (envoie email de refus avec raison)

**Page Détail Institution** (`/admin/institutions/{id}`):
- Header: Logo + Nom + Statut (editable)
- Tabs:
  1. **Informations Générales**:
     - Form editable: Nom, adresse, contact, etc.
     - Historique modifications
  2. **Utilisateurs**:
     - Liste des utilisateurs liés (InstitutionUser)
     - Bouton "Inviter utilisateur"
  3. **Clés Cryptographiques**:
     - Liste des clés (status, dates, fingerprint)
     - Actions: Révoquer clé
  4. **Documents**:
     - Liste paginée des documents signés
     - Statistiques: Total | Actifs | Révoqués
  5. **Audit**:
     - Logs d'actions liées à cette institution

---

##### 3.2.3 Gestion des Clés Cryptographiques (`/admin/keys`)
**Objectif**: Surveiller, révoquer, auditer les clés

**Vue Liste**:
- Filtres:
  - Institution (autocomplete)
  - Statut (Active | Expiring Soon | Expired | Revoked)
  - Algorithm (RSA 4096 | ECDSA P-384)
  - Date expiration (range)
- Tableau:
  - Institution
  - Fingerprint (tronqué, tooltip complet)
  - Algorithm
  - Créée le
  - Expire le (badge rouge si <30j)
  - Statut
  - Nb docs signés
  - Actions: Voir détail | Révoquer

**Modal Révocation de Clé**:
- Avertissement: "Cette action est IRRÉVERSIBLE et invalidera tous les documents signés avec cette clé"
- Dropdown: Raison
  - Clé compromise
  - Demande de l'institution
  - Expiration forcée
  - Autre
- Textarea: Détails
- Checkbox: "Notifier l'institution par email"
- Bouton "Confirmer la Révocation" (rouge, désactivé jusqu'à confirmation)

**Page Détail Clé**:
- Informations:
  - Clé publique (format PEM, copyable)
  - Fingerprint (multiple formats: SHA-256, MD5)
  - Dates de création/expiration
  - Clé parente (si rotation)
  - Validée par (admin)
- Documents signés avec cette clé (liste)
- Timeline de rotation (si applicable)
- Bouton actions: Révoquer | Export metadata

---

##### 3.2.4 Gestion des Signalements (`/admin/reports`)
**Objectif**: Traiter les signalements de documents suspects

**Vue Kanban** (3 colonnes):
1. **Pending** (à traiter)
2. **Under Review** (en cours)
3. **Closed** (traités)

**Card Signalement** (draggable):
- Badge type: Fake | Altered | Unauthorized
- Document hash (tronqué)
- Institution concernée
- Signalé le + par (IP/email)
- Raison (extrait)
- Bouton "Traiter"

**Modal Traitement Signalement**:
- **Section Informations**:
  - Document hash complet
  - Institution émettrice (lien)
  - Historique vérifications du document
  - Raison complète du signalement
  - Preuves jointes (screenshots)
- **Section Enquête**:
  - Bouton "Vérifier le document maintenant"
  - Historique des signalements similaires
  - Logs d'audit du document
- **Section Actions**:
  - Radio: Décision
    - ⚠️ Confirmer comme frauduleux (révoque document)
    - ✓ Rejeter le signalement (non fondé)
    - 🔍 Mettre en attente (enquête en cours)
  - Textarea: Notes administrateur
  - Checkbox: "Notifier l'institution"
  - Checkbox: "Notifier le signaleur" (si email fourni)
- Boutons:
  - "Valider la décision"
  - "Fermer sans action"

**Filtres** (barre latérale):
- Statut
- Type de signalement
- Institution
- Date (range)

---

##### 3.2.5 Gestion des Utilisateurs (`/admin/users`)
**Objectif**: Gérer les comptes utilisateurs (admins, institutions, public)

**Tableau**:
- Colonnes:
  - Email
  - Nom complet
  - Rôle (badge: Admin | Institution | Public)
  - Statut (Pending | Active | Suspended)
  - Institution(s) liée(s)
  - Dernière connexion
  - Actions

**Actions**:
- Éditer rôle
- Suspendre/Activer
- Réinitialiser mot de passe
- Voir logs d'audit
- Supprimer (avec confirmation)

**Modal Édition Utilisateur**:
- Informations de base (email, nom, téléphone)
- Dropdown rôle
- Dropdown statut
- Liste institutions associées (si rôle Institution)
- Checkbox "2FA activé"
- Historique des connexions (10 dernières)

---

##### 3.2.6 Statistiques & Rapports (`/admin/analytics`)
**Objectif**: Vue d'ensemble et export de données

**Layout**: Grille de widgets configurables

**Widgets disponibles**:
1. **Vérifications Globales**:
   - Line chart avec filtres temporels
   - Breakdown: Succès/Échecs/Révoqués
   - Export CSV

2. **Top Institutions**:
   - Classement par nb de vérifications
   - Classement par nb de documents signés
   - Table exportable

3. **Performance Système**:
   - Temps de réponse API (P50, P95, P99)
   - Taux d'erreur
   - Disponibilité (uptime)

4. **Géolocalisation**:
   - Carte interactive (Plotly) des vérifications par pays
   - Top 10 pays

5. **Tendances de Fraude**:
   - Évolution signalements
   - Taux de confirmation fraude
   - Institutions les plus ciblées

**Génération de Rapports**:
- Form:
  - Dropdown: Type de rapport
    - Rapport mensuel complet
    - Rapport par institution
    - Rapport de fraude
    - Rapport de performance
  - Date range picker
  - Multiselect: Institutions (optionnel)
  - Checkbox: Inclure graphiques
- Bouton "Générer" → PDF téléchargeable

---

##### 3.2.7 Logs d'Audit (`/admin/audit`)
**Objectif**: Consultation complète des logs système

**Interface de Recherche Avancée**:
- Filtres multiples (combinables):
  - User (autocomplete)
  - Action type (multiselect)
  - Resource type (multiselect)
  - Date range (picker)
  - IP address (input)
  - Success/Failure (toggle)
  - Recherche full-text dans details (input)

**Tableau des Logs**:
- Colonnes:
  - Timestamp (tri par défaut desc)
  - User (lien vers profil)
  - Action (badge coloré selon type)
  - Resource (type + ID lié)
  - IP Address
  - Status (✓/✗)
  - Détails (expandable)
- Pagination: 50/100/200 items

**Row Expansion** (click sur ligne):
- JSON formaté des details
- User agent complet
- Stack trace (si erreur)
- Bouton "Voir logs connexes" (même user/resource dans ±1h)

**Export**:
- Bouton "Exporter résultats"
  - Format: CSV | JSON | PDF
  - Limite: 10,000 lignes max

**Composants**:
- Table (Shadcn UI) avec virtual scrolling
- DateRangePicker
- Multiselect (react-select)

---

### 3.3 Interface Application Desktop (Flet/Python)

#### Objectif
Application native cross-platform (Windows/macOS/Linux) pour institutions: génération et gestion locale des clés, signature de documents, synchronisation des métadonnées avec le backend.

#### Principes de Sécurité
- ⚠️ **CRITIQUE**: Clés privées JAMAIS transmises au serveur
- Stockage local sécurisé: Keyring (Windows DPAPI, macOS Keychain, Linux SecretService)
- Communication API: HTTPS uniquement, tokens JWT
- Logs locaux chiffrés

---

##### 3.3.1 Écran de Connexion/Inscription
**Layout**: Centré, minimaliste

**Mode Connexion**:
- Logo Let's Check (centré)
- Titre: "Connexion Institution"
- Form:
  - TextField email (validation email)
  - TextField password (obscured, toggle visibility)
  - Checkbox "Se souvenir de moi"
- Bouton "Se Connecter" (primaire, pleine largeur)
- Lien "Mot de passe oublié?"
- Divider + Texte "Pas encore inscrit?"
- Bouton "Créer un compte institution" (secondaire)

**Mode Inscription**:
- Titre: "Inscription Institution"
- Form (étapes):
  1. **Informations Institution**:
     - TextField: Nom institution
     - Dropdown: Type institution
     - TextField: Pays (dropdown searchable)
     - TextField: Adresse
  2. **Contact**:
     - TextField: Email professionnel
     - TextField: Téléphone
     - TextField: Site web (optionnel)
  3. **Authentification**:
     - TextField: Mot de passe (règles affichées)
     - TextField: Confirmation mot de passe
     - Checkbox: "J'accepte les CGU"
- Bouton "Créer le compte"
- Note: "Votre compte sera validé sous 24-48h par notre équipe"

**2FA Setup** (si activé après 1ère connexion):
- QR code TOTP (Google Authenticator, Authy)
- Code de secours (à sauvegarder)
- Input: Code de vérification
- Bouton "Activer 2FA"

**Interactions**:
- Validation temps réel des champs
- ProgressRing pendant requête API
- SnackBar pour erreurs (email déjà utilisé, etc.)

**Composants Flet**:
```python
ft.TextField(label="Email", keyboard_type=ft.KeyboardType.EMAIL)
ft.ElevatedButton("Se Connecter", on_click=handle_login)
ft.ProgressRing() # pendant loading
ft.SnackBar(content=ft.Text("Erreur de connexion"))
```

---

##### 3.3.2 Dashboard Principal
**Layout**: Sidebar + Zone principale

**Sidebar** (navigation):
- Header: Logo + Nom institution (tronqué si long)
- Menu items (icons + texte):
  - 🏠 Tableau de Bord
  - 🔑 Mes Clés
  - ✍️ Signer Document
  - 📄 Documents Signés
  - 🔄 Backup & Rotation
  - ⚙️ Paramètres
- Footer: User info + Bouton déconnexion

**Zone Principale - Dashboard**:

**Section Statistiques** (3 cards):
1. **Documents Signés**:
   - Chiffre total
   - Graphique sparkline 7 derniers jours
2. **Vérifications**:
   - Nb de vérifications sur mes docs
   - Badge: "+23% vs mois dernier"
3. **Clé Active**:
   - Fingerprint (tronqué)
   - Expire dans: X jours (badge rouge si <30)
   - Bouton "Voir détails"

**Section Actions Rapides** (boutons en grille 2x2):
- "Signer un Document" (primaire)
- "Générer Nouvelle Clé"
- "Vérifier un Document"
- "Voir l'Historique"

**Section Alertes** (si applicable):
- Liste d'alertes:
  - ⚠️ "Votre clé expire dans 15 jours - Planifier rotation"
  - 🔔 "3 nouveaux signalements sur vos documents"
  - ✅ "Backup automatique effectué avec succès"

**Section Activité Récente** (liste):
- Timeline des 10 dernières actions:
  - "Document 'Diplôme_2024.pdf' signé"
  - "Clé rotated avec succès"
  - Timestamp relatif (il y a 2h, hier, etc.)

**Composants Flet**:
```python
ft.Card(content=ft.Column([
    ft.Text("Documents Signés", weight=ft.FontWeight.BOLD),
    ft.Text("1,234", size=32)
]))
ft.ElevatedButton("Signer un Document", icon=ft.icons.EDIT)
ft.ListTile(
    leading=ft.Icon(ft.icons.CHECK_CIRCLE, color=ft.colors.GREEN),
    title=ft.Text("Document signé"),
    subtitle=ft.Text("Il y a 2 heures")
)
```

---

##### 3.3.3 Gestion des Clés Cryptographiques
**Page "Mes Clés"**:

**Vue Liste des Clés**:
- Tableau:
  - Statut (icône colorée)
  - Fingerprint (tronqué, tooltip complet au hover)
  - Algorithme (RSA 4096 / ECDSA P-384)
  - Créée le
  - Expire le (badge rouge si <30j)
  - Actions (dropdown):
    - Voir détails
    - Exporter clé publique
    - Révoquer

**Bouton "Générer Nouvelle Clé"** → Dialog:

**Dialog Génération de Clé**:
- Titre: "Créer une Nouvelle Clé Cryptographique"
- Form:
  - Dropdown Algorithm:
    - RSA 4096 (recommandé) - Description: "Standard industrie, compatible"
    - ECDSA P-384 (avancé) - Description: "Plus rapide, clés plus petites"
  - Slider Durée validité:
    - 6 mois | 1 an | 2 ans | 3 ans (défaut: 1 an)
    - Note: "Rotation automatique recommandée tous les ans"
  - TextField: Nom/Label clé (optionnel, pour identification)
  - TextField: Mot de passe protection locale (obligatoire)
    - Confirmation mot de passe
    - PasswordStrengthMeter (visuel)
- Checkbox: "Sauvegarder un backup chiffré automatiquement"
- **Processus**:
  1. Bouton "Générer" (désactivé jusqu'à mot de passe fort)
  2. ProgressBar animé: "Génération en cours..." (peut prendre 5-10s)
  3. Étapes affichées:
     - ✓ Génération paire de clés
     - ✓ Chiffrement clé privée
     - ✓ Stockage local sécurisé (Keyring)
     - ✓ Synchronisation métadonnées au serveur
  4. Success Dialog:
     - "Clé générée avec succès!"
     - Fingerprint affiché
     - Bouton "Télécharger Backup" (fichier .p12 chiffré)
     - Bouton "Copier Clé Publique"
     - Note: "Conservez précieusement votre mot de passe et le backup"

**Page Détail d'une Clé**:
- **Section Informations**:
  - Fingerprint (multiple formats)
  - Algorithme + Taille
  - Dates: Création, Expiration
  - Statut actuel
  - Nb de documents signés avec cette clé
- **Section Clé Publique**:
  - Affichage format PEM (scrollable, monospace)
  - Boutons: Copier | Exporter (.pem) | Partager (QR code)
- **Section Sécurité**:
  - Historique d'utilisation (dernières signatures)
  - Tentatives de connexion avec cette clé
  - Bouton "Changer mot de passe de protection"
- **Actions**:
  - Bouton "Révoquer cette clé" (rouge, confirmation requise)

**Modal Révocation de Clé**:
- Avertissement: "Révoquer cette clé invalidera tous les documents signés avec elle!"
- Dropdown: Raison
  - Rotation planifiée (recommandé si vous avez une nouvelle clé)
  - Clé compromise
  - Changement de politique
  - Autre
- Textarea: Détails
- Checkbox: "J'ai sauvegardé un backup de mes documents importants"
- Checkbox: "Je comprends que cette action est irréversible"
- Bouton "Confirmer la Révocation" (rouge, désactivé jusqu'à coches)

---

##### 3.3.4 Signature de Documents
**Page "Signer un Document"**:

**Section 1: Sélection du Document**:
- Zone drag-and-drop stylisée (comme web):
  - "Glissez votre document ici ou cliquez pour parcourir"
  - Formats: PDF, JPG, PNG, DOCX (max 50MB)
- Preview document (si image/PDF):
  - Miniature + nom fichier
  - Taille + type
  - Bouton "Changer de document"

**Section 2: Options de Signature**:
- Dropdown: "Clé à utiliser"
  - Liste des clés ACTIVE
  - Affiche: Nom + Fingerprint + Expire le
- Checkbox Options:
  - ✓ "Ajouter un QR code au document"
    - Position: Coin bas-droit | Bas-gauche | Haut-droit | Personnalisé
    - Taille: Petit (2cm) | Moyen (3cm) | Grand (5cm)
  - ✓ "Utiliser la stéganographie" (si image)
    - Méthode: DCT (recommandé) | LSB (legacy)
    - Force: Faible | Moyenne | Forte
    - Note: "La stéganographie cache la signature dans l'image"
  - ☐ "Ajouter un watermark visible"
    - Upload logo institution
    - Texte personnalisé
  - ✓ "Générer un certificat de signature" (PDF)

**Section 3: Métadonnées** (optionnel):
- TextField: Titre du document
- TextField: Description
- Dropdown: Catégorie (Diplôme, Certificat, Attestation, etc.)
- DatePicker: Date d'expiration du document (optionnel)
- Tags: Labels personnalisés (multi-input)

**Processus de Signature**:
1. Bouton "Signer le Document" (vert, grand)
2. Dialog de confirmation:
   - Résumé des options choisies
   - Input: Mot de passe de la clé (pour déverrouiller clé privée locale)
   - Checkbox: "J'atteste que ce document est authentique"
3. Clic "Confirmer" → ProgressBar avec étapes:
   - ✓ Calcul hash SHA-256 du document
   - ✓ Signature cryptographique (locale)
   - ✓ Ajout QR code (si activé)
   - ✓ Application stéganographie (si activé)
   - ✓ Génération certificat
   - ✓ Envoi métadonnées au serveur (SANS clé privée)
   - ✓ Enregistrement document signé localement
4. Success Dialog:
   - "Document signé avec succès!"
   - Hash document: XXXXX (copyable)
   - QR code affiché (scannable pour vérification immédiate)
   - Boutons:
     - "Télécharger Document Signé" (avec QR/watermark)
     - "Télécharger Certificat" (PDF)
     - "Partager le Lien de Vérification" (URL courte)
     - "Signer un Autre Document"

**Gestion des Erreurs**:
- Si clé expirée: "Clé expirée - Générez une nouvelle clé"
- Si document trop lourd: "Taille max 50MB - Compressez votre fichier"
- Si échec réseau: "Métadonnées sauvegardées localement - Réessayez plus tard"

---

##### 3.3.5 Historique des Documents Signés
**Page "Documents Signés"**:

**Filtres** (barre supérieure):
- Search: Recherche par nom/hash
- Dropdown: Statut (Tous | Actifs | Révoqués | Expirés)
- DateRangePicker: Période de signature
- Dropdown: Catégorie

**Vue Liste** (DataTable):
- Colonnes:
  - Thumbnail (si image)
  - Nom fichier
  - Hash (tronqué)
  - Signé le
  - Clé utilisée (fingerprint)
  - Statut (badge)
  - Nb vérifications
  - Actions (dropdown):
    - Voir détails
    - Télécharger original
    - Télécharger certificat
    - Révoquer
    - Partager lien

**Page Détail Document**:
- **Section Général**:
  - Preview (si PDF/image)
  - Informations: Nom, taille, type, hash complet
  - Métadonnées: Titre, description, catégorie, tags
  - QR code (si présent)
- **Section Signature**:
  - Clé utilisée (lien vers détail clé)
  - Date signature
  - Algorithme
  - Signature vérifiable (bouton "Vérifier maintenant")
- **Section Vérifications** (tableau):
  - Liste des vérifications effectuées sur ce document
  - Colonnes: Date, IP, Méthode, Résultat
  - Graphique: Vérifications par jour (7 derniers jours)
- **Section Sécurité**:
  - Historique modifications
  - Signalements (si existants)
  - Bouton "Télécharger Rapport d'Audit"

**Modal Révocation de Document**:
- Titre: "Révoquer le Document"
- Avertissement: "Ce document ne sera plus reconnu comme valide"
- Dropdown: Raison
  - Document annulé/remplacé
  - Erreur dans le document
  - Demande du bénéficiaire
  - Clé compromise
  - Autre
- Textarea: Explication détaillée
- Checkbox: "Notifier automatiquement les vérificateurs récents"
- Bouton "Confirmer la Révocation"

---

##### 3.3.6 Backup et Rotation Automatique
**Page "Backup & Rotation"**:

**Section Backup**:
- **Status Actuel**:
  - Dernier backup: Date + heure
  - Nb de clés sauvegardées
  - Taille totale backup
  - Emplacement: C:\Users\...\letscheck\backups\
- **Configuration**:
  - Checkbox: "Backup automatique hebdomadaire"
  - Dropdown: Jour de la semaine
  - Slider: "Conserver les N derniers backups" (1-10)
  - TextField: Chemin personnalisé (avec bouton parcourir)
- **Actions**:
  - Bouton "Créer Backup Maintenant"
  - Bouton "Restaurer depuis Backup"

**Process Backup**:
1. Dialog: "Entrez le mot de passe de chiffrement du backup"
   - TextField password (confirmation requise)
   - Note: "Ce mot de passe est DIFFÉRENT des mots de passe de vos clés"
2. ProgressBar: "Chiffrement en cours..."
3. Success: "Backup créé: backup_YYYYMMDD_HHMMSS.enc"
   - Bouton "Ouvrir le dossier"

**Process Restauration**:
1. FilePicker: Sélection fichier .enc
2. Dialog: "Entrez le mot de passe du backup"
3. Validation + déchiffrement
4. Liste des clés trouvées dans le backup
5. Checkboxes: Sélection des clés à restaurer
6. Bouton "Restaurer"
7. Success: "X clés restaurées avec succès"

**Section Rotation Automatique**:
- **Configuration**:
  - Checkbox: "Rotation automatique des clés"
  - Dropdown: Fréquence
    - Tous les 6 mois
    - Tous les ans (recommandé)
    - Tous les 2 ans
  - Checkbox: "M'avertir 30 jours avant rotation"
  - Checkbox: "Créer backup avant rotation"
- **Prochaine Rotation Planifiée**:
  - Date affichée en grand
  - Countdown: "Dans 45 jours"
  - Bouton "Forcer Rotation Maintenant"
- **Historique Rotations**:
  - Liste: Date | Ancienne clé → Nouvelle clé | Raison

**Process Rotation Manuelle**:
1. Dialog warning: "Préparez-vous à générer une nouvelle clé"
2. Étapes guidées:
   - Création nouvelle clé (réutilise dialog génération)
   - Marquage ancienne clé comme ROTATED
   - Synchronisation serveur
   - Backup automatique
   - Email notification aux admins
3. Success: "Rotation terminée - Nouvelle clé active"

---

##### 3.3.7 Paramètres
**Page "Paramètres"**:

**Tabs**:

**Tab 1: Profil Institution**:
- Form editable:
  - Nom institution
  - Email contact
  - Téléphone
  - Site web
  - Logo (upload)
- Bouton "Sauvegarder les Modifications"

**Tab 2: Sécurité**:
- **Authentification**:
  - Bouton "Changer le Mot de Passe"
  - Toggle: "Activer 2FA"
  - Liste: "Sessions Actives"
    - Affiche: Appareil, IP, Dernière activité
    - Bouton "Déconnecter" par session
- **Clés**:
  - Dropdown: "Algorithme par défaut" (RSA 4096 / ECDSA P-384)
  - Slider: "Durée validité par défaut" (6m - 3ans)
  - Toggle: "Exiger mot de passe fort pour clés"

**Tab 3: Notifications**:
- Checkboxes:
  - ☐ Email quand clé expire dans 30 jours
  - ☐ Email quand document vérifié
  - ☐ Email quand document révoqué
  - ☐ Email quand signalement reçu
  - ☐ Notifications desktop pour alertes critiques

**Tab 4: Avancé**:
- **Stockage Local**:
  - Affiche: Espace utilisé (X MB)
  - Bouton "Nettoyer les Logs Anciens"
  - Bouton "Réinitialiser Application" (supprime données locales)
- **Logs**:
  - Toggle: "Activer logs de debug"
  - Bouton "Exporter Logs" (.zip)
  - Bouton "Voir Logs en Direct" (console)
- **API**:
  - TextField: "URL Serveur" (pour custom deployment)
  - TextField: "Token API" (readonly, copyable)
  - Bouton "Régénérer Token"

**Tab 5: À Propos**:
- Version application
- Changelog (expandable)
- Liens:
  - Documentation
  - Support
  - Signaler un Bug
  - CGU & Politique de confidentialité
- Bouton "Vérifier les Mises à Jour"

---

## 4. Flux de Données Détaillés

### 4.1 Flux Signature (Desktop → Backend)

```
1. UTILISATEUR ACTION:
   - Sélectionne document local (file picker)
   
2. APPLICATION DESKTOP (Flet):
   a. Calcul hash SHA-256 (hashlib Python)
   b. Récupération clé privée depuis Keyring (nécessite mot de passe user)
   c. Signature cryptographique locale:
      - RSA: RSA-PSS avec MGF1-SHA256
      - ECDSA: ECDSA-SHA384
   d. Génération QR code (qrcode library):
      - Données: {"hash": "...", "verify_url": "..."}
   e. Application stéganographie (si image):
      - DCT embedding avec clé de chiffrement
   
3. ENVOI MÉTADONNÉES (HTTPS POST):
   Request:
   {
     "document_hash": "abc123...",
     "signature": "base64_signature",
     "public_key_fingerprint": "def456...",
     "file_type": "PDF",
     "qr_data": {...},
     "metadata": {
       "original_filename": "diplome.pdf",
       "file_size": 2048576,
       "has_steganography": true,
       "steganography_method": "DCT"
     }
   }
   
4. BACKEND (Django):
   a. Validation token JWT
   b. Vérification institution active
   c. Validation clé publique existe et active
   d. Vérification hash unique (pas de doublon)
   e. Création SignedDocument en DB
   f. Log audit: SIGN action
   
5. RESPONSE:
   {
     "success": true,
     "document_id": "uuid",
     "verification_url": "https://letscheck.cm/verify/abc123",
     "qr_code_url": "https://letscheck.cm/qr/abc123",
     "certificate_url": "https://letscheck.cm/cert/uuid.pdf"
   }
   
6. APPLICATION DESKTOP:
   - Sauvegarde document signé localement
   - Affiche success dialog avec QR code
   - Optionnel: Upload document signé vers cloud storage
```

### 4.2 Flux Vérification (Public Web → Backend)

```
1. UTILISATEUR ACTION:
   - Upload document via interface web
   
2. FRONTEND (React):
   a. Lecture fichier (FileReader API)
   b. Calcul hash côté client (Web Crypto API):
      ```javascript
      const buffer = await file.arrayBuffer();
      const hashBuffer = await crypto.subtle.digest('SHA-256', buffer);
      const hashHex = Array.from(new Uint8Array(hashBuffer))
        .map(b => b.toString(16).padStart(2, '0'))
        .join('');
      ```
   c. Affichage ProgressBar
   
3. ENVOI REQUÊTE (HTTPS POST):
   Request:
   {
     "document_hash": "abc123...",
     "method": "UPLOAD",
     "verifier_ip": "192.168.1.1" // Ajouté par backend
   }
   
4. BACKEND (Django View):
   a. Rate limiting check (max 10 vérif/min/IP)
   b. Recherche SignedDocument par hash (index DB):
      ```python
      try:
          document = SignedDocument.objects.select_related(
              'institution', 'key'
          ).get(document_hash=provided_hash)
      except SignedDocument.DoesNotExist:
          return Response({"result": "NOT_FOUND"})
      ```
   c. Validations:
      - Document.status == ACTIVE?
      - Key.status == ACTIVE?
      - Key.expires_at > now()?
      - Vérification signature cryptographique:
        ```python
        from cryptography.hazmat.primitives import hashes
        from cryptography.hazmat.primitives.asymmetric import padding, rsa
        
        public_key = serialization.load_pem_public_key(
            document.key.public_key.encode()
        )
        
        try:
            public_key.verify(
                base64.b64decode(document.signature),
                provided_hash.encode(),
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            result = "AUTHENTIC"
        except InvalidSignature:
            result = "INVALID_SIGNATURE"
        ```
   d. Création DocumentVerification log
   e. Génération certificat PDF (si authentique):
      - Template avec logo institution
      - Informations document + date vérification
      - QR code pour re-vérification
   f. Création AuditLog
   
5. RESPONSE:
   {
     "result": "AUTHENTIC",
     "document": {
       "institution": {
         "name": "Université de Yaoundé",
         "logo_url": "...",
         "country": "CM"
       },
       "signed_at": "2024-06-15T10:30:00Z",
       "key_algorithm": "RSA_4096",
       "file_type": "PDF"
     },
     "certificate_url": "https://letscheck.cm/certificates/uuid.pdf",
     "verification_id": "uuid"
   }
   
6. FRONTEND:
   - Affichage Card résultat (vert/rouge selon result)
   - Bouton download certificat
   - Mise à jour historique local (localStorage)
```

### 4.3 Flux Rotation de Clé (Desktop → Backend)

```
1. DÉCLENCHEMENT:
   - Auto: Cron job quotidien vérifie expires_at
   - Manuel: User clique "Forcer Rotation"
   
2. APPLICATION DESKTOP:
   a. Vérification prérequis:
      - Institution ACTIVE
      - Au moins une clé ACTIVE existante
   b. Génération nouvelle paire de clés (même process que création initiale)
   c. Liaison parent_key:
      new_key.parent_key = old_key
   d. Chiffrement et stockage local nouvelle clé privée
   
3. ENVOI BACKEND (HTTPS POST):
   Request:
   {
     "old_key_id": "uuid_old",
     "new_public_key": "-----BEGIN PUBLIC KEY-----...",
     "new_fingerprint": "sha256_new",
     "algorithm": "RSA_4096",
     "rotation_type": "SCHEDULED",
     "reason": "Rotation automatique annuelle"
   }
   
4. BACKEND (Transaction atomique):
   a. Validation old_key appartient à institution
   b. Création CryptographicKey (new_key):
      - status = ACTIVE
      - parent_key = old_key
   c. Update old_key:
      - status = ROTATED
   d. Création KeyRotation log
   e. Email notification aux admins institution
   f. AuditLog
   
5. RESPONSE:
   {
     "success": true,
     "new_key_id": "uuid_new",
     "old_key_status": "ROTATED"
   }
   
6. APPLICATION DESKTOP:
   - Backup automatique (avec ancienne et nouvelle clé)
   - Notification user: "Rotation réussie"
   - Update UI: nouvelle clé marquée ACTIVE
```

---

## 5. Sécurité et Conformité

### 5.1 Principes de Sécurité

**Cryptographie**:
- Clés: RSA-4096 ou ECDSA P-384 minimum
- Hash: SHA-256 pour documents
- Signature: RSA-PSS ou ECDSA
- Chiffrement backup: AES-256-GCM

**Stockage Clés Privées**:
- Jamais sur serveur (principe fondamental)
- Desktop: Keyring system-specific
  - Windows: DPAPI
  - macOS: Keychain
  - Linux: SecretService (libsecret)
- Protection par mot de passe fort (PBKDF2, 100k iterations)

**Communication**:
- HTTPS/TLS 1.3 minimum
- Certificate pinning dans l'app desktop
- JWT tokens courts (1h) avec refresh tokens
- Rate limiting agressif:
  - Vérifications: 10/min/IP
  - Login: 5 tentatives/15min
  - API: 100 req/min/user

**Base de Données**:
- Chiffrement at-rest (PostgreSQL TDE)
- Backups chiffrés (AES-256)
- Accès restreint par rôle (RLS PostgreSQL)

### 5.2 Conformité RGPD

**Données Collectées**:
- Minimisation: Seulement nécessaires
- Consentement explicite pour emails marketing

**Droits Utilisateurs**:
- Droit d'accès: Export JSON de toutes données
- Droit à l'oubli: Suppression compte + données (sauf logs audit légaux)
- Droit de portabilité: Export format standard

**Audit**:
- Logs immuables de toutes opérations
- Rétention: 5 ans pour conformité légale
- Accès administrateur tracé

**DPO**:
- Contact: dpo@letscheck.cm
- Formulaire réclamation intégré

---

## 6. Déploiement et Scalabilité

### 6.1 Architecture de Déploiement

```
┌─────────────────────────────────────────────────────┐
│              LOAD BALANCER (Nginx)                  │
│           SSL Termination + Routing                 │
└───────────────────┬─────────────────────────────────┘
                    │
        ┌───────────┴───────────┐
        │                       │
        ▼                       ▼
┌──────────────┐        ┌──────────────┐
│  Django App  │        │  Django App  │
│  Instance 1  │        │  Instance 2  │
│  (Gunicorn)  │        │  (Gunicorn)  │
└──────┬───────┘        └──────┬───────┘
       │                       │
       └───────────┬───────────┘
                   │
       ┌───────────┴───────────┐
       │                       │
       ▼                       ▼
┌─────────────┐         ┌─────────────┐
│ PostgreSQL  │         │    Redis    │
│  Primary    │◄───────►│   Cache     │
└──────┬──────┘         └─────────────┘
       │
       ▼
┌─────────────┐
│ PostgreSQL  │
│  Replica    │
└─────────────┘
```

**Composants**:
- **Nginx**: Reverse proxy, SSL, rate limiting, static files
- **Django Apps**: 2+ instances pour haute disponibilité
- **PostgreSQL**: Primary + réplica read pour scalabilité
- **Redis**: Cache sessions, rate limiting, Celery broker
- **Celery Workers**: Tâches async (emails, stats, rotations)

### 6.2 Docker Compose (Development)

```yaml
version: '3.8'

services:
  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: letscheck_dev
      POSTGRES_USER: letscheck
      POSTGRES_PASSWORD: dev_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  web:
    build:
      context: .
      dockerfile: Dockerfile
    command: python manage.py runserver 0.0.0.0:8000
    volumes:
      - .:/app
    ports:
      - "8000:8000"
    depends_on:
      - db
      - redis
    environment:
      - DEBUG=True
      - DATABASE_URL=postgresql://letscheck:dev_password@db:5432/letscheck_dev
      - REDIS_URL=redis://redis:6379/0
      - SECRET_KEY=dev_secret_key

  celery:
    build:
      context: .
      dockerfile: Dockerfile
    command: celery -A config worker -l info
    volumes:
      - .:/app
    depends_on:
      - db
      - redis
    environment:
      - DATABASE_URL=postgresql://letscheck:dev_password@db:5432/letscheck_dev
      - REDIS_URL=redis://redis:6379/0

volumes:
  postgres_data:
```

### 6.3 Scalabilité (BNF-04: 10k institutions, 1M vérif/jour)

**Stratégies**:

1. **Horizontal Scaling**:
   - Django apps: Auto-scaling (Kubernetes/ECS)
   - Règle: Si CPU > 70%, spawn +1 instance

2. **Database Optimization**:
   - Indexes stratégiques (sur hashes, dates)
   - Partitioning par date (tables audit, verifications)
   - Connection pooling (PgBouncer)
   - Queries optimisées (select_related, prefetch_related)

3. **Caching**:
   - Redis pour:
     - Sessions utilisateurs
     - Rate limiting counters
     - Clés publiques fréquentes
     - Statistiques agrégées
   - TTL adapté par donnée (1h-24h)

4. **CDN**:
   - Static files (JS, CSS, images): CloudFlare
   - Certificats PDF générés: S3 + CloudFront
   - QR codes: Cache CDN

5. **Async Processing**:
   - Celery pour:
     - Envoi emails (batches de 1000)
     - Génération certificats PDF
     - Calcul statistiques journalières
     - Rotation automatique clés
   - Priority queues: critical > normal > low

**Estimations Performance**:
- 1M vérifications/jour = ~12 verif/seconde
- Avec 4 instances Django (4 cores chacune): 50-100 req/s
- DB: PostgreSQL peut handle 10k-50k queries/s
- Redis: 100k ops/s
→ Architecture largement suffisante

---

## 7. Workflows et Cas d'Usage

### 7.1 Workflow Institution (Onboarding)

```
1. Inscription Desktop App
   → Institution remplit formulaire
   → Email de confirmation envoyé
   → Status: PENDING

2. Validation Admin
   → Admin reçoit notification
   → Vérification documents légaux
   → Validation ou refus
   → Email envoyé à institution

3. Première Génération de Clé
   → Institution génère clé RSA-4096
   → Clé privée stockée localement
   → Métadonnées clé publique sync au serveur
   → Status institution: ACTIVE

4. Première Signature
   → Institution signe document test
   → Vérification immédiate sur web public
   → Feedback: "Votre système fonctionne!"

5. Utilisation Normale
   → Signature documents en masse
   → Monitoring statistiques
   → Rotations automatiques
```

### 7.2 Workflow Citoyen (Vérification)

```
1. Réception Document (email/physique)
   → Citoyen veut vérifier authenticité

2. Accès Interface Publique
   → https://letscheck.cm/verify

3. Upload ou Scan
   → Choix méthode (fichier, QR, hash)
   → Soumission

4. Résultat Immédiat
   → Authentique: Download certificat
   → Invalide: Explication + option signalement
   → Non trouvé: Contact institution

5. (Optionnel) Signalement
   → Si suspicion fraude
   → Form signalement
   → Admin notifié
```

### 7.3 Workflow Admin (Gestion Fraude)

```
1. Réception Signalement
   → Email + notification dashboard
   → Signalement: Status PENDING

2. Enquête
   → Consultation document
   → Vérification historique
   → Contact institution si nécessaire

3. Décision
   → Si frauduleux:
     - Révocation document
     - Notification institution
     - Possiblement: Suspension compte
   → Si non fondé:
     - Rejet signalement
     - Notification signaleur (si email)

4. Suivi
   → Statistiques fraudes détectées
   → Rapports mensuels
   → Amélioration détection
```

---

## 8. Tests et Qualité

### 8.1 Tests Backend (Django)

```python
# apps/documents/tests/test_verification.py

from django.test import TestCase
from apps.documents.models import SignedDocument
from apps.cryptography.models import CryptographicKey

class VerificationTestCase(TestCase):
    def setUp(self):
        # Création fixtures: institution, clé, document
        self.institution = Institution.objects.create(...)
        self.key = CryptographicKey.objects.create(...)
        self.document = SignedDocument.objects.create(...)
    
    def test_authentic_document_verification(self):
        """Vérification document authentique retourne AUTHENTIC"""
        response = self.client.post('/api/verify/', {
            'document_hash': self.document.document_hash
        })
        self.assertEqual(response.data['result'], 'AUTHENTIC')
    
    def test_invalid_hash_returns_not_found(self):
        """Hash inexistant retourne NOT_FOUND"""
        response = self.client.post('/api/verify/', {
            'document_hash': 'invalid_hash_123'
        })
        self.assertEqual(response.data['result'], 'NOT_FOUND')
    
    def test_revoked_document_verification(self):
        """Document révoqué retourne REVOKED"""
        self.document.status = 'REVOKED'
        self.document.save()
        response = self.client.post('/api/verify/', {
            'document_hash': self.document.document_hash
        })
        self.assertEqual(response.data['result'], 'REVOKED')
    
    def test_rate_limiting(self):
        """Rate limiting bloque après 10 requêtes"""
        for i in range(10):
            self.client.post('/api/verify/', {...})
        response = self.client.post('/api/verify/', {...})
        self.assertEqual(response.status_code, 429)
```

**Tests Requis**:
- Unit tests: Models, views, serializers (couverture >80%)
- Integration tests: Workflows complets
- Performance tests: Temps réponse <3s (BNF-02)
- Security tests: Injection SQL, XSS, CSRF

### 8.2 Tests Frontend (React)

```javascript
// src/components/VerificationForm.test.jsx

import { render, screen, fireEvent } from '@testing-library/react';
import VerificationForm from './VerificationForm';

test('affiche formulaire upload par défaut', () => {
  render(<VerificationForm />);
  expect(screen.getByText(/glissez votre document/i)).toBeInTheDocument();
});

test('calcule hash et appelle API au submit', async () => {
  const mockFile = new File(['content'], 'test.pdf', { type: 'application/pdf' });
  render(<VerificationForm />);
  
  const input = screen.getByLabelText(/upload/i);
  fireEvent.change(input, { target: { files: [mockFile] } });
  
  const button = screen.getByText(/vérifier/i);
  fireEvent.click(button);
  
  // Vérifier que hash calculé et API appelée
  await waitFor(() => {
    expect(mockApiCall).toHaveBeenCalledWith({
      document_hash: expect.any(String)
    });
  });
});

test('affiche résultat authentique correctement', async () => {
  mockApiCall.mockResolvedValue({ result: 'AUTHENTIC', ... });
  render(<VerificationForm />);
  
  // Trigger vérification...
  
  await waitFor(() => {
    expect(screen.getByText(/authentique/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /télécharger certificat/i }))
      .toBeInTheDocument();
  });
});
```

### 8.3 Tests Desktop App (Flet)

```python
# tests/test_key_generation.py

import unittest
from app.crypto import KeyGenerator

class TestKeyGeneration(unittest.TestCase):
    def test_generate_rsa_4096_key(self):
        """Génération clé RSA 4096 réussit"""
        gen = KeyGenerator()
        private_key, public_key = gen.generate_rsa(4096)
        
        self.assertIsNotNone(private_key)
        self.assertIsNotNone(public_key)
        self.assertEqual(private_key.key_size, 4096)
    
    def test_sign_and_verify(self):
        """Signature puis vérification réussit"""
        gen = KeyGenerator()
        private_key, public_key = gen.generate_rsa(2048)
        
        message = b"Test document hash"
        signature = gen.sign(private_key, message)
        
        is_valid = gen.verify(public_key, message, signature)
        self.assertTrue(is_valid)
    
    def test_local_storage_encryption(self):
        """Stockage local chiffre correctement"""
        storage = SecureStorage()
        test_key = "test_private_key_pem"
        password = "strong_password_123"
        
        storage.store_key("test_key", test_key, password)
        retrieved = storage.retrieve_key("test_key", password)
        
        self.assertEqual(retrieved, test_key)
```

---

## 9. Métriques de Succès (KPIs)

### 9.1 Métriques Techniques

| Métrique | Cible | Mesure |
|----------|-------|--------|
| Temps vérification | <3s | P95 response time API |
| Disponibilité | 99.9% | Uptime monitoring |
| Taux erreur | <0.1% | Failed requests / Total |
| Scalabilité | 1M verif/jour | Load testing |
| Sécurité | 0 breaches | Audit logs + penetration tests |

### 9.2 Métriques Métier

| Métrique | Cible Année 1 | Mesure |
|----------|---------------|--------|
| Institutions actives | 100 | DB count |
| Documents signés | 50,000 | DB count |
| Vérifications | 500,000 | DB count |
| Taux fraude détecté | <1% | Signalements confirmés / Total |
| Satisfaction | >90% | Surveys NPS |

---

## 10. Roadmap de Développement

### Phase 1: Backend + Admin (Mois 1-2)
- [x] Setup projet Django + structure apps
- [x] Modèles de données + migrations
- [x] Authentication (JWT + 2FA)
- [x] API REST (DRF):
  - Endpoints institutions
  - Endpoints clés (métadonnées)
  - Endpoints documents
  - Endpoints vérifications
- [x] Système d'audit (AuditLog)
- [x] Django Admin customisé
- [x] Celery tasks (emails, stats)
- [x] Tests unitaires (>80% coverage)

### Phase 2: Interface Publique Web (Mois 2-3)
- [x] Setup React + Inertia.js
- [x] Composants UI (Shadcn + Tailwind):
  - Composants réutilisables
  - Thème cohérent
- [x] Pages publiques:
  - Accueil
  - Vérification (3 méthodes)
  - Résultats vérification
  - FAQ
- [x] Intégration APIs backend
- [x] Hash côté client (Web Crypto API)
- [x] Génération certificats PDF
- [x] Responsive design + accessibilité
- [x] Tests E2E (Playwright)

### Phase 3: Application Desktop (Mois 3-4)
- [x] Setup Flet (Python)
- [x] Écrans:
  - Login/Inscription
  - Dashboard
  - Génération clés
  - Signature documents
  - Gestion clés
  - Backup/Rotation
  - Paramètres
- [x] Cryptographie locale:
  - Génération clés RSA/ECDSA
  - Signature documents
  - Stockage sécurisé (Keyring)
- [x] QR code generation
- [x] Stéganographie (DCT)
- [x] Sync API backend
- [x] Auto-update système
- [x] Packaging (Windows/macOS/Linux)

### Phase 4: Optimisation & Production (Mois 4-5)
- [x] Performance tuning:
  - Query optimization
  - Caching stratégique
  - CDN setup
- [x] Security hardening:
  - Penetration testing
  - Corrections vulnérabilités
  - Rate limiting fine-tuning
- [x] Monitoring:
  - Sentry (error tracking)
  - Prometheus + Grafana (metrics)
  - ELK Stack (logs)
- [x] Documentation:
  - API docs (Swagger)
  - User guides (FR/EN)
  - Admin manual
- [x] Load testing (1M verif/day)
- [x] Déploiement production

### Phase 5: Lancement & Itération (Mois 5-6)
- [x] Beta test (10 institutions pilotes)
- [x] Feedback collection
- [x] Bug fixes
- [x] Campagne marketing
- [x] Onboarding premières institutions
- [x] Support 24/7
- [x] Itérations basées feedback

---

## 11. Considérations Techniques Importantes

### 11.1 Gestion des Formats de Documents

**Formats Supportés** (BF-03):
- PDF: Utilisation de PyPDF2 pour extraction métadonnées
- Images (JPEG, PNG): Pillow pour traitement + stéganographie DCT
- DOCX: python-docx pour lecture
- XML: lxml parser

**Hash Calculation**:
```python
# Backend (Django)
import hashlib

def calculate_document_hash(file):
    """Calcule SHA-256 du contenu brut du fichier"""
    hasher = hashlib.sha256()
    for chunk in file.chunks():
        hasher.update(chunk)
    return hasher.hexdigest()

# Frontend (JavaScript)
async function calculateHash(file) {
  const buffer = await file.arrayBuffer();
  const hashBuffer = await crypto.subtle.digest('SHA-256', buffer);
  return Array.from(new Uint8Array(hashBuffer))
    .map(b => b.toString(16).padStart(2, '0'))
    .join('');
}

# Desktop (Python)
def calculate_hash(filepath):
    hasher = hashlib.sha256()
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            hasher.update(chunk)
    return hasher.hexdigest()
```

### 11.2 QR Code Implementation

**Génération (Desktop)**:
```python
import qrcode
import json

def generate_verification_qr(document_hash, institution_name):
    data = {
        'hash': document_hash,
        'verify_url': f'https://letscheck.cm/verify?hash={document_hash}',
        'institution': institution_name,
        'version': '1.0'
    }
    
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(json.dumps(data))
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    return img
```

**Scan (Web/Mobile)**:
```javascript
// Utilisation de html5-qrcode library
import { Html5Qrcode } from "html5-qrcode";

const scanner = new Html5Qrcode("qr-reader");
scanner.start(
  { facingMode: "environment" },
  {
    fps: 10,
    qrbox: { width: 250, height: 250 }
  },
  (decodedText) => {
    const data = JSON.parse(decodedText);
    // Redirection vers vérification avec hash
    window.location.href = data.verify_url;
  }
);
```

### 11.3 Stéganographie (Images)

**Embedding (Desktop)**:
```python
from PIL import Image
import numpy as np
from scipy.fftpack import dct, idct

def embed_signature_dct(image_path, signature_data, output_path):
    """
    Embed signature dans coefficients DCT de l'image
    Résistant aux compressions légères
    """
    img = Image.open(image_path).convert('RGB')
    img_array = np.array(img)
    
    # Conversion YCbCr
    ycbcr = rgb_to_ycbcr(img_array)
    
    # DCT sur canal Y (luminance)
    dct_y = dct(dct(ycbcr[:,:,0], axis=0, norm='ortho'), axis=1, norm='ortho')
    
    # Embedding dans coefficients mid-frequency
    signature_bits = ''.join(format(ord(c), '08b') for c in signature_data)
    
    for i, bit in enumerate(signature_bits[:1000]):  # Max 1000 bits
        x, y = get_dct_position(i)  # Positions mid-freq
        if bit == '1':
            dct_y[x, y] += 5  # Ajustement contrôlé
        else:
            dct_y[x, y] -= 5
    
    # IDCT et reconstruction
    modified_y = idct(idct(dct_y, axis=1, norm='ortho'), axis=0, norm='ortho')
    ycbcr[:,:,0] = modified_y
    
    img_modified = Image.fromarray(ycbcr_to_rgb(ycbcr).astype('uint8'))
    img_modified.save(output_path, quality=95)
```

**Extraction (Backend/Desktop)**:
```python
def extract_signature_dct(image_path):
    """Extrait signature depuis image stéganographiée"""
    # Inverse du processus embedding
    # Retourne signature si trouvée, None sinon
    pass
```

### 11.4 Certificat de Vérification PDF

**Génération (Backend)**:
```python
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from datetime import datetime

def generate_verification_certificate(document, verification):
    """
    Génère PDF de certification de vérification
    Inclut: Logo, infos document, QR code, timestamp
    """
    filename = f"certificate_{verification.id}.pdf"
    c = canvas.Canvas(filename, pagesize=A4)
    width, height = A4
    
    # Header avec logo Let's Check
    logo = ImageReader('static/logo.png')
    c.drawImage(logo, 50, height-100, width=100, height=80)
    
    c.setFont("Helvetica-Bold", 24)
    c.drawString(200, height-70, "Certificat de Vérification")
    
    # Infos document
    c.setFont("Helvetica", 12)
    y = height - 150
    
    c.drawString(50, y, f"Document Hash: {document.document_hash}")
    y -= 30
    c.drawString(50, y, f"Institution: {document.institution.name}")
    y -= 30
    c.drawString(50, y, f"Signé le: {document.created_at.strftime('%d/%m/%Y %H:%M')}")
    y -= 30
    c.drawString(50, y, f"Vérifié le: {verification.timestamp.strftime('%d/%m/%Y %H:%M')}")
    y -= 30
    
    # Résultat avec couleur
    c.setFillColorRGB(0, 0.8, 0)  # Vert
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, y, f"Résultat: AUTHENTIQUE ✓")
    y -= 50
    
    # QR Code pour re-vérification
    qr_img = generate_verification_qr(document.document_hash, document.institution.name)
    c.drawImage(ImageReader(qr_img), 50, y-150, width=150, height=150)
    
    # Footer
    c.setFont("Helvetica", 8)
    c.drawString(50, 50, f"Ce certificat a été généré automatiquement par Let's Check")
    c.drawString(50, 35, f"Vérifiez à nouveau sur: https://letscheck.cm/verify")
    
    c.save()
    return filename
```

### 11.5 Rate Limiting Intelligent

**Implementation (Django Middleware)**:
```python
from django.core.cache import cache
from django.http import JsonResponse
import time

class RateLimitMiddleware:
    """
    Rate limiting basé sur IP avec tiers (normal/premium/admin)
    """
    LIMITS = {
        'anonymous': {'requests': 10, 'window': 60},  # 10/min
        'authenticated': {'requests': 100, 'window': 60},  # 100/min
        'institution': {'requests': 1000, 'window': 60},  # 1000/min
    }
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Déterminer tier utilisateur
        if request.user.is_authenticated:
            if request.user.role == 'INSTITUTION':
                tier = 'institution'
            else:
                tier = 'authenticated'
        else:
            tier = 'anonymous'
        
        # Clé cache: IP + endpoint
        ip = self.get_client_ip(request)
        cache_key = f"ratelimit:{tier}:{ip}:{request.path}"
        
        # Incrément compteur
        requests = cache.get(cache_key, 0)
        limit = self.LIMITS[tier]
        
        if requests >= limit['requests']:
            return JsonResponse({
                'error': 'Rate limit exceeded',
                'retry_after': limit['window']
            }, status=429)
        
        # Incrément avec expiration
        cache.set(cache_key, requests + 1, limit['window'])
        
        response = self.get_response(request)
        
        # Headers informatifs
        response['X-RateLimit-Limit'] = limit['requests']
        response['X-RateLimit-Remaining'] = limit['requests'] - requests - 1
        
        return response
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
```

---

## 12. Recommandations Finales

### 12.1 Best Practices à Suivre

**Code Quality**:
- PEP 8 (Python) et ESLint (JavaScript)
- Type hints Python (mypy)
- Docstrings complètes
- Code reviews obligatoires
- Pre-commit hooks (black, flake8, prettier)

**Git Workflow**:
- Branches: `main` (prod), `develop` (staging), `feature/*`
- Commits conventionnels: `feat:`, `fix:`, `docs:`, etc.
- Pull requests avec review
- CI/CD avec GitHub Actions

**Documentation**:
- README.md à jour
- CONTRIBUTING.md pour contributeurs
- API docs auto-générées (drf-spectacular)
- Architecture Decision Records (ADR)

### 12.2 Pièges à Éviter

❌ **Ne JAMAIS**:
- Stocker clés privées sur serveur
- Logger mots de passe ou tokens
- Exposer stack traces en production
- Déployer sans tests
- Hardcoder secrets dans le code
- Ignorer les migrations Django

✅ **Toujours**:
- Valider inputs utilisateur
- Utiliser HTTPS partout
- Chiffrer données sensibles
- Faire des backups réguliers
- Monitorer les performances
- Auditer les accès

### 12.3 Évolution Future

**Features Potentielles (Post-V1)**:
- Blockchain integration (immuabilité supplémentaire)
- IA détection fraudes (ML sur patterns de signalement)
- Support formats additionnels (ODT, EPUB)
- Mobile apps natives (iOS/Android)
- API publique pour intégrations tierces (BF-08)
- Multi-signature (co-signing)
- Timestamping RFC 3161
- Watermarking avancé
- Internationalisation complète (AR, ES, DE)

---

## 13. Conclusion

Cette architecture propose une solution **complète, sécurisée et scalable** pour Let's Check :

### Points Forts:
✅ **Sécurité maximale**: Clés privées jamais exposées, cryptographie robuste  
✅ **Performance**: <3s vérification, support 1M req/jour  
✅ **Modularité**: Apps Django indépendantes, faciles à maintenir  
✅ **UX excellent**: Interfaces simples pour tous utilisateurs  
✅ **Conformité**: RGPD, audit complet, traçabilité totale  
✅ **Scalabilité**: Architecture horizontale, caching intelligent  

### Prochaines Étapes:
1. **Semaine 1-2**: Setup backend Django + modèles
2. **Semaine 3-4**: APIs REST + admin
3. **Semaine 5-6**: Interface publique React
4. **Semaine 7-10**: Application desktop Flet
5. **Semaine 11-12**: Tests, optimisation, déploiement

**Équipe Recommandée**:
- 1 Backend dev (Django/Python) - Lead
- 1 Frontend dev (React/TypeScript)
- 1 Desktop dev (Python/Flet)
- 1 DevOps (Docker, CI/CD)
- 1 Designer UI/UX (part-time)
- 1 QA Tester (part-time)

**Budget Estimé** (5 mois):
- Développement: $50k-80k
- Infrastructure (1ère année): $5k-10k
- Marketing/Legal: $10k-20k
- **Total**: $65k-110k

---

**Contact & Support**:
- Documentation: https://docs.letscheck.cm
- Support: support@letscheck.cm
- GitHub: https://github.com/letscheck/platform

*Document créé le: 2024-12-14*  
*Version: 1.0.0*  
*Auteur: Architecture Team*