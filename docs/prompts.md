# Guide Complet de Développement - Let's Check

## 📋 Instructions Générales

**Contexte du Projet:**
- Application de vérification d'authenticité de documents
- **Projet Django déjà initialisé et configuré**
- Backend: Django 5.x avec Django Ninja pour les APIs
- Frontend: React 18+ avec Inertia.js dans `frontend/`
- Base de données: PostgreSQL (configurée)
- Tâches asynchrones: Huey (configuré)
- UI Framework: Shadcn UI + Tailwind CSS
- **Document de référence obligatoire**: `docs/letscheck_architecture.md`

**Architecture Communication:**
- Frontend (`frontend/`) ↔ Backend Django via **Inertia.js** (pour pages web)
- APIs Django Ninja = **uniquement pour app desktop et intégrations tierces**
- Appels API depuis frontend possible pour traitements spécifiques

**Règles Importantes:**
- ⚠️ **Toujours consulter** `docs/letscheck_architecture.md` avant de coder
- ✅ Tâches courtes et focalisées (1 modèle ou 1 service à la fois)
- ✅ Inclure docstrings et comments en français
- ✅ Suivre l'architecture exacte du document
- ✅ Créer les fichiers dans la structure définie

---

# PARTIE 1: BACKEND DJANGO

## 🎯 Phase 1: Modèles Core

### Prompt 1.1: Modèle User

```
Contexte: Projet Let's Check déjà initialisé. Frontend dans frontend/ (Inertia).

Tâche: Crée uniquement le modèle User étendu.

Fichier: apps/core/models/user.py

Référence: Consulte la section "2.1 App: core (Fondation) - User" dans docs/letscheck_architecture.md

Spécifications exactes du document:
- Copie fidèlement la structure du modèle décrite
- Respecte tous les champs, choices, et indexes
- UUID primary key
- Ajoute docstring complète en français

Créé aussi apps/core/models/__init__.py avec import User
```

### Prompt 1.2: Modèle AuditLog

```
Contexte: Projet Let's Check. Frontend géré par Inertia dans frontend/.

Tâche: Crée uniquement le modèle AuditLog.

Fichier: apps/core/models/audit.py

Référence: Section "2.1 App: core - AuditLog" dans docs/letscheck_architecture.md

Points critiques:
- Modèle IMMUABLE (ajoute manager custom pour empêcher update/delete)
- Respecte exactement tous les ActionType et ResourceType du document
- Tous les indexes listés
- JSONField pour details

Mets à jour apps/core/models/__init__.py
```

### Prompt 1.3: Modèle EmailTemplate

```
Contexte: Let's Check - frontend dans frontend/ (Inertia).

Tâche: Crée le modèle EmailTemplate uniquement.

Fichier: apps/core/models/email_template.py

Référence: Section "2.1 App: core" dans docs/letscheck_architecture.md (cherche EmailTemplate)

Spécifications:
- Templates emails multilingues (fr/en)
- Champs: name, template_type, subject, body_text, body_html, language, active
- Docstring complète

Mets à jour __init__.py
```

---

## 🎯 Phase 2: Services Core

### Prompt 2.1: Service AuditService

```
Contexte: Let's Check - modèles Core créés. Frontend: frontend/ (Inertia).

Tâche: Crée AuditService avec méthodes de logging.

Fichier: apps/core/services/audit_service.py

Référence: Section "1.4 Flux de Données Principaux - Flux 3: Audit" dans docs/letscheck_architecture.md

Méthodes requises:
- log_login(user, ip, success)
- log_document_sign(user, document, ip)
- log_document_verify(document_hash, ip, result)
- log_key_created(user, key, ip)
- log_institution_validated(admin, institution, ip)

Chaque méthode crée un AuditLog avec le bon ActionType.
Gestion d'erreurs silencieuse (try/except, logging).

Créé aussi apps/core/services/__init__.py
```

### Prompt 2.2: Service EmailService

```
Contexte: Let's Check - modèles Core prêts. Frontend: frontend/ (Inertia).

Tâche: Crée EmailService pour envoi emails avec templates.

Fichier: apps/core/services/email_service.py

Référence: Cherche "EmailTemplate" et "envoi emails" dans docs/letscheck_architecture.md

Méthodes:
- send_verification_email(user, verification_url)
- send_welcome_email(institution_user)
- send_document_revoked_email(institution, document)
- send_key_expiring_email(institution, key, days_remaining)

Utilise EmailTemplate.objects.get() pour récupérer templates.
Rendering avec django.template.
Log erreurs d'envoi.

Mets à jour __init__.py
```

### Prompt 2.3: Tâche Huey - Envoi Emails Asynchrone

```
Contexte: Let's Check - EmailService créé. Frontend: frontend/ (Inertia).

Tâche: Crée tâche Huey pour envoi emails async.

Fichier: apps/core/tasks.py

Référence: Section "1.3 Stack Technologique - Huey" dans docs/letscheck_architecture.md

Spécifications:
- Fonction send_email_async() décorée avec @task()
- Paramètres: to_email, subject, body_text, body_html
- Utilise django.core.mail.send_mail()
- Retry automatique (3 tentatives)

Exemple:
```python
from huey.contrib.djhuey import task

@task(retries=3)
def send_email_async(to_email, subject, body_text, body_html):
    # Code envoi
    pass
```

Modifier EmailService pour utiliser cette tâche.
```

---

## 🎯 Phase 3: Modèles Institutions

### Prompt 3.1: Modèle Institution

```
Contexte: Let's Check - Core terminé. Frontend: frontend/ (Inertia).

Tâche: Crée uniquement le modèle Institution.

Fichier: apps/institutions/models/institution.py

Référence: Section "2.2 App: institutions" dans docs/letscheck_architecture.md

Copie exactement:
- Tous les champs (name, legal_name, slug, type, adresse, etc.)
- Type choices (PUBLIC, PRIVATE, etc.)
- Status choices (PENDING, ACTIVE, etc.)
- Tous les indexes listés
- validated_by FK vers User

Docstring complète.
Créé apps/institutions/models/__init__.py
```

### Prompt 3.2: Modèle InstitutionUser

```
Contexte: Let's Check - Institution model créé. Frontend: frontend/ (Inertia).

Tâche: Crée le modèle InstitutionUser.

Fichier: apps/institutions/models/institution_user.py

Référence: Section "2.2 App: institutions - InstitutionUser" dans docs/letscheck_architecture.md

Spécifications exactes du document:
- FK institution et user
- Role choices (ADMIN, SIGNER, AUDITOR, VIEWER)
- unique_together sur (institution, user)
- invited_by FK

Mets à jour __init__.py
```

---

## 🎯 Phase 4: Services Institutions

### Prompt 4.1: Service InstitutionService

```
Contexte: Let's Check - modèles Institutions prêts. Frontend: frontend/ (Inertia).

Tâche: Crée InstitutionService.

Fichier: apps/institutions/services/institution_service.py

Référence: Section "2.2 App: institutions" + "Workflow Institution" dans docs/letscheck_architecture.md

Méthodes requises:
- validate_institution(institution, admin_user)
  * Change status PENDING → ACTIVE
  * Set validated_by et validated_at
  * Envoie email via EmailService
  * Log audit via AuditService

- suspend_institution(institution, admin_user, reason)
- get_institution_stats(institution)
- invite_user(institution, email, role, invited_by)

Créé apps/institutions/services/__init__.py
```

---

## 🎯 Phase 5: Modèles Cryptography

### Prompt 5.1: Modèle CryptographicKey

```
Contexte: Let's Check - Institutions OK. Frontend: frontend/ (Inertia).

Tâche: Crée le modèle CryptographicKey.

Fichier: apps/cryptography/models/cryptographic_key.py

Référence: Section "2.3 App: cryptography" dans docs/letscheck_architecture.md

IMPORTANT: Stocke UNIQUEMENT clés publiques, jamais privées.

Spécifications exactes:
- FK institution
- public_key (TextField PEM)
- fingerprint (unique)
- Algorithm choices (RSA_2048, RSA_4096, ECDSA_P256, ECDSA_P384)
- Status choices (ACTIVE, EXPIRING_SOON, EXPIRED, REVOKED, ROTATED)
- parent_key (Self FK) pour rotation
- Tous les indexes

Créé apps/cryptography/models/__init__.py
```

### Prompt 5.2: Modèle KeyRotation

```
Contexte: Let's Check - CryptographicKey créé. Frontend: frontend/ (Inertia).

Tâche: Crée le modèle KeyRotation.

Fichier: apps/cryptography/models/key_rotation.py

Référence: Section "2.3 App: cryptography - KeyRotation" dans docs/letscheck_architecture.md

Spécifications:
- FK old_key et new_key
- RotationType choices (SCHEDULED, MANUAL, SECURITY, COMPROMISED)
- performed_by FK User
- reason TextField

Mets à jour __init__.py
```

---

## 🎯 Phase 6: Services Cryptography

### Prompt 6.1: Service CryptographyService

```
Contexte: Let's Check - modèles Crypto OK. Frontend: frontend/ (Inertia).

Tâche: Crée CryptographyService.

Fichier: apps/cryptography/services/cryptography_service.py

Référence: Section "2.3 App: cryptography" + "11.1 Gestion des Formats" dans docs/letscheck_architecture.md

Méthodes:
- validate_public_key(public_key_pem, algorithm) → bool
- calculate_fingerprint(public_key_pem) → str (SHA-256)
- verify_signature(public_key_pem, message, signature) → bool
- register_key_metadata(institution, public_key_pem, algorithm, expires_at)
- rotate_key(old_key, new_public_key_pem, reason, user)

Utilise cryptography library.
Créé apps/cryptography/services/__init__.py
```

### Prompt 6.2: Tâche Huey - Monitoring Expiration Clés

```
Contexte: Let's Check - CryptographyService créé. Frontend: frontend/ (Inertia).

Tâche: Crée tâche Huey pour monitoring expiration clés.

Fichier: apps/cryptography/tasks.py

Référence: Section "2.3 App: cryptography" dans docs/letscheck_architecture.md

Spécifications:
- Tâche périodique quotidienne (00:05)
- Vérifie clés ACTIVE
- Si expire dans 30j → status EXPIRING_SOON + email
- Si expirée → status EXPIRED + email urgence

Exemple:
```python
from huey import crontab
from huey.contrib.djhuey import periodic_task

@periodic_task(crontab(hour='0', minute='5'))
def monitor_key_expiration():
    # Code vérification
    pass
```
```

---

## 🎯 Phase 7: Modèles Documents

### Prompt 7.1: Modèle SignedDocument

```
Contexte: Let's Check - Crypto terminé. Frontend: frontend/ (Inertia).

Tâche: Crée le modèle SignedDocument.

Fichier: apps/documents/models/signed_document.py

Référence: Section "2.4 App: documents" dans docs/letscheck_architecture.md

Spécifications exactes:
- FK institution et key (PROTECT)
- document_hash (unique, indexed) - SHA-256
- signature (TextField base64)
- FileType choices (PDF, JPEG, PNG, DOCX, XML)
- Status choices (ACTIVE, REVOKED, EXPIRED, SUSPENDED)
- QR et stéganographie: qr_code_data, has_steganography, steganography_method
- revoked_by FK, revocation_reason
- Tous indexes listés

Créé apps/documents/models/__init__.py
```

### Prompt 7.2: Modèle DocumentVerification

```
Contexte: Let's Check - SignedDocument créé. Frontend: frontend/ (Inertia).

Tâche: Crée le modèle DocumentVerification.

Fichier: apps/documents/models/document_verification.py

Référence: Section "2.4 App: documents - DocumentVerification" dans docs/letscheck_architecture.md

Spécifications:
- FK document (nullable)
- provided_hash
- Method choices (UPLOAD, QR_SCAN, HASH_INPUT, STEGANOGRAPHY, API)
- Result choices (AUTHENTIC, INVALID_SIGNATURE, NOT_FOUND, REVOKED, EXPIRED, KEY_EXPIRED)
- verifier_ip, verifier_user_agent, verifier_country
- verification_duration_ms, certificate_url
- Tous indexes

Mets à jour __init__.py
```

---

## 🎯 Phase 8: Services Documents

### Prompt 8.1: Service DocumentService

```
Contexte: Let's Check - modèles Documents OK. Frontend: frontend/ (Inertia).

Tâche: Crée DocumentService.

Fichier: apps/documents/services/document_service.py

Référence: Section "2.4 App: documents" + "4.1 Flux Signature" dans docs/letscheck_architecture.md

Méthodes:
- register_signed_document(institution, key, document_hash, signature, file_type, metadata)
  * Valide institution active
  * Valide clé active
  * Vérifie hash unique
  * Vérifie signature avec CryptographyService
  * Crée SignedDocument
  * Log audit

- verify_document(document_hash, verifier_ip, method='UPLOAD')
  * Recherche document
  * Valide status
  * Vérifie signature
  * Crée DocumentVerification
  * Retourne dict résultat

- revoke_document(document, user, reason)

Créé apps/documents/services/__init__.py
```

### Prompt 8.2: Service CertificateService

```
Contexte: Let's Check - DocumentService créé. Frontend: frontend/ (Inertia).

Tâche: Crée CertificateService pour PDF certificats.

Fichier: apps/documents/services/certificate_service.py

Référence: Section "11.4 Certificat de Vérification PDF" dans docs/letscheck_architecture.md

Méthode principale:
- generate_verification_certificate(document, verification) → str (URL)
  * Génère PDF avec ReportLab
  * Contenu: logo, infos document, QR code, date vérification
  * Sauvegarde dans media/certificates/
  * Retourne URL

Utilise reportlab et qrcode libraries.
Mets à jour __init__.py
```

---

## 🎯 Phase 9: Modèles Verifications

### Prompt 9.1: Modèles VerificationRequest et SuspiciousReport

```
Contexte: Let's Check - Documents OK. Frontend: frontend/ (Inertia).

Tâche: Crée VerificationRequest ET SuspiciousReport.

Fichiers:
- apps/verifications/models/verification_request.py
- apps/verifications/models/suspicious_report.py

Référence: Section "2.5 App: verifications" dans docs/letscheck_architecture.md

VerificationRequest:
- document_hash, uploader_ip, user_agent
- Status choices (SUCCESS, FAILURE, ERROR)
- Indexes sur (document_hash, timestamp), (uploader_ip, timestamp)

SuspiciousReport:
- FK document (nullable), document_hash
- ReportType choices (FAKE, ALTERED, UNAUTHORIZED, OTHER)
- Status choices (PENDING, UNDER_REVIEW, CONFIRMED, REJECTED, CLOSED)
- reporter_ip, reporter_email, reporter_name
- reviewed_by FK, admin_notes

Créé apps/verifications/models/__init__.py
```

---

## 🎯 Phase 10: Services Verifications

### Prompt 10.1: Service VerificationService

```
Contexte: Let's Check - modèles Verifications OK. Frontend: frontend/ (Inertia).

Tâche: Crée VerificationService.

Fichier: apps/verifications/services/verification_service.py

Référence: Section "2.5 App: verifications" + "4.2 Flux Vérification" dans docs/letscheck_architecture.md

Méthodes:
- process_verification_request(document_hash, ip, user_agent, method)
  * Crée VerificationRequest
  * Appelle DocumentService.verify_document()
  * Mesure processing_time_ms
  * Retourne résultat formaté

- create_suspicious_report(document_hash, report_type, reason, reporter_ip, reporter_email=None)
  * Rate limit: max 3/IP/jour (Redis)
  * Crée SuspiciousReport
  * Notifie admins si FAKE

- get_document_verification_history(document_hash, limit=10)

Créé apps/verifications/services/__init__.py
```

---

## 🎯 Phase 11: Modèles Analytics

### Prompt 11.1: Modèles Statistic et PerformanceMetric

```
Contexte: Let's Check - Verifications terminé. Frontend: frontend/ (Inertia).

Tâche: Crée Statistic ET PerformanceMetric.

Fichiers:
- apps/analytics/models/statistic.py
- apps/analytics/models/performance_metric.py

Référence: Section "2.6 App: analytics" dans docs/letscheck_architecture.md

Statistic:
- FK institution (nullable)
- MetricType choices (VERIF_TOTAL, VERIF_SUCCESS, DOC_SIGNED, etc.)
- Period choices (HOURLY, DAILY, WEEKLY, MONTHLY, YEARLY)
- period_start, period_end, value (BigInt)
- breakdown (JSONField)
- unique_together sur (institution, metric_type, period_type, period_start)

PerformanceMetric:
- endpoint, method
- avg_response_time_ms, p95, p99
- request_count, error_count

Créé apps/analytics/models/__init__.py
```

---

## 🎯 Phase 12: Services Analytics

### Prompt 12.1: Service AnalyticsService

```
Contexte: Let's Check - modèles Analytics OK. Frontend: frontend/ (Inertia).

Tâche: Crée AnalyticsService.

Fichier: apps/analytics/services/analytics_service.py

Référence: Section "2.6 App: analytics" dans docs/letscheck_architecture.md

Méthodes:
- aggregate_daily_stats(date)
  * Agrège stats jour précédent
  * Crée Statistic pour chaque metric_type
  * Global + par institution

- get_dashboard_stats(institution=None) → dict
  * Retourne stats dashboard

- get_verification_trends(days=30, institution=None) → dict
  * Pour graphiques
  * Format: {dates: [], success: [], failed: []}

- calculate_fraud_rate(period, institution=None) → float

Cache Redis (TTL 1h) pour stats fréquentes.
Créé apps/analytics/services/__init__.py
```

### Prompt 12.2: Tâche Huey - Agrégation Quotidienne

```
Contexte: Let's Check - AnalyticsService créé. Frontend: frontend/ (Inertia).

Tâche: Crée tâche Huey agrégation stats quotidienne.

Fichier: apps/analytics/tasks.py

Référence: Section "2.6 App: analytics" dans docs/letscheck_architecture.md

Spécifications:
- Tâche périodique quotidienne (00:05)
- Appelle AnalyticsService.aggregate_daily_stats() pour jour précédent
- Agrège: VERIFICATIONS, DOCUMENTS, KEYS, REPORTS, INSTITUTIONS
- Global + par institution

Exemple:
```python
from huey import crontab
from huey.contrib.djhuey import periodic_task
from datetime import timedelta
from django.utils import timezone

@periodic_task(crontab(hour='0', minute='5'))
def aggregate_daily_statistics():
    from apps.analytics.services import AnalyticsService
    date = timezone.now().date() - timedelta(days=1)
    AnalyticsService.aggregate_daily_stats(date)
```
```

---

## 🎯 Phase 13: APIs Django Ninja (Desktop App)

### Prompt 13.1: Schemas Ninja - Base

```
Contexte: Let's Check - Backend presque complet. Frontend: frontend/ (Inertia).
Les APIs sont UNIQUEMENT pour app desktop.

Tâche: Crée schemas Ninja pour Institution et CryptographicKey.

Fichiers:
- apps/institutions/schemas.py
- apps/cryptography/schemas.py

Référence: Section "2.2 Institutions" et "2.3 Cryptography" dans docs/letscheck_architecture.md

Utilise ninja.Schema (Pydantic).

InstitutionSchema:
- Champs publics seulement
- logo_url (computed)

CryptographicKeySchema:
- Exclut clé privée (n'existe pas serveur)
- id, fingerprint, algorithm, status, dates

Exemple:
```python
from ninja import Schema
from datetime import datetime

class InstitutionSchema(Schema):
    id: str
    name: str
    type: str
    status: str
    # ...
```
```

### Prompt 13.2: Schemas Ninja - Documents

```
Contexte: Let's Check - Schemas base créés. Frontend: frontend/ (Inertia).
APIs pour desktop uniquement.

Tâche: Crée schemas Ninja pour Documents.

Fichier: apps/documents/schemas.py

Référence: Section "2.4 App: documents" dans docs/letscheck_architecture.md

Schemas:
- SignedDocumentSchema (lecture)
- SignedDocumentCreateSchema (création depuis desktop)
  * document_hash, signature, key_id, file_type, metadata
  * Validation: hash unique, signature base64
- DocumentVerificationSchema

Exemple:
```python
from ninja import Schema
from typing import Optional, Dict

class SignedDocumentCreateSchema(Schema):
    document_hash: str
    signature: str
    key_id: str
    file_type: str
    metadata: Optional[Dict] = None
```
```

### Prompt 13.3: Router Ninja - Institutions

```
Contexte: Let's Check - Schemas prêts. Frontend: frontend/ (Inertia).
API pour desktop uniquement.

Tâche: Crée router Ninja pour Institutions.

Fichier: apps/api/routers/institution_router.py

Référence: Section "7.3 API Ninja - Desktop App Endpoints" dans docs/letscheck_architecture.md

Endpoints:
- GET /api/institutions/me (institution de l'user)
- PATCH /api/institutions/me (update infos)
- GET /api/institutions/me/stats

Utilise ninja.Router avec auth JWT.
Appelle InstitutionService pour logique.

Exemple:
```python
from ninja import Router
from ninja.security import HttpBearer

router = Router(tags=["Institutions"])

@router.get("/me", auth=HttpBearer())
def get_my_institution(request):
    # Code
    pass
```

Créé apps/api/routers/__init__.py
```

### Prompt 13.4: Router Ninja - Keys

```
Contexte: Let's Check - Router Institution créé. Frontend: frontend/ (Inertia).

Tâche: Crée router Ninja pour Keys.

Fichier: apps/api/routers/key_router.py

Référence: Section "7.3 API Ninja - Desktop App Endpoints" dans docs/letscheck_architecture.md

Endpoints:
- GET /api/keys (liste clés institution)
- POST /api/keys (enregistrer métadonnées nouvelle clé)
- POST /api/keys/{id}/rotate (rotation)

Auth JWT.
Appelle CryptographyService.

Mets à jour __init__.py
```

### Prompt 13.5: Router Ninja - Documents

```
Contexte: Let's Check - Routers Institution/Keys OK. Frontend: frontend/ (Inertia).

Tâche: Crée router Ninja pour Documents.

Fichier: apps/api/routers/document_router.py

Référence: Section "7.3 API Ninja - Desktop App Endpoints" dans docs/letscheck_architecture.md

Endpoints:
- GET /api/documents (liste, filtré par institution)
- POST /api/documents (enregistrer document signé)
- POST /api/documents/{id}/revoke

Auth JWT.
Appelle DocumentService.

Mets à jour __init__.py
```

### Prompt 13.6: Router Ninja - Public Verify

```
Contexte: Let's Check - Routers desktop OK. Frontend: frontend/ (Inertia).

Tâche: Crée router Ninja PUBLIC pour vérification.

Fichier: apps/api/routers/public_router.py

Référence: Section "4.2 Flux Vérification" et "7.4 API Publique Ninja" dans docs/letscheck_architecture.md

Endpoint:
- POST /api/public/verify (SANS auth, public)
  * Body: {document_hash, method}
  * Rate limiting: 10 req/min/IP
  * Appelle VerificationService
  * Retourne résultat complet

Ce endpoint est utilisé par frontend Inertia aussi.

Mets à jour __init__.py
```

### Prompt 13.7: API Principale Ninja

```
Contexte: Let's Check - Tous routers créés. Frontend: frontend/ (Inertia).

Tâche: Crée API principale Ninja qui regroupe tous routers.

Fichier: apps/api/api.py

Référence: Section configuration dans docs/letscheck_architecture.md

Spécifications:
- Créé NinjaAPI instance
- Add tous les routers:
  * /institutions/ → institution_router
  * /keys/ → key_router
  * /documents/ → document_router
  * /public/ → public_router
- Titre: "Let's Check API"
- Version: "1.0.0"

Exemple:
```python
from ninja import NinjaAPI
from apps.api.routers import (
    institution_router, 
    key_router, 
    document_router, 
    public_router
)

api = NinjaAPI(
    title="Let's Check API",
    version="1.0.0",
    description="API pour app desktop et intégrations"
)

api.add_router("/institutions/", institution_router)
# ...
```

Ajoute dans config/urls.py:
```python
from apps.api.api import api

urlpatterns = [
    path("api/", api.urls),
    # ...
]
```
```

---

## 🎯 Phase 14: Middlewares et Permissions

### Prompt 14.1: Middleware Rate Limiting

```
Contexte: Let's Check - APIs créées. Frontend: frontend/ (Inertia).

Tâche: Crée middleware rate limiting intelligent.

Fichier: apps/core/middleware/rate_limit_middleware.py

Référence: Section "11.5 Rate Limiting Intelligent" dans docs/letscheck_architecture.md

Spécifications:
- Limites par tier:
  * Anonymous: 10 req/min
  * Authenticated: 100 req/min
  * Institution: 1000 req/min
- Stockage Redis
- Headers X-RateLimit-Limit, X-RateLimit-Remaining
- Response 429 si dépassé

Exemple structure:
```python
class RateLimitMiddleware:
    LIMITS = {
        'anonymous': {'requests': 10, 'window': 60},
        # ...
    }
    
    def __call__(self, request):
        # Code rate limiting
        pass
```

Ajoute à settings MIDDLEWARE.
```

### Prompt 14.2: Permissions Custom

```
Contexte: Let's Check - Middleware créé. Frontend: frontend/ (Inertia).

Tâche: Crée permissions custom Django.

Fichier: apps/core/permissions.py

Référence: Document architecture sections permissions

Permissions:
- IsInstitutionUser (User.role == INSTITUTION et institution active)
- IsInstitutionAdmin (InstitutionUser.role == ADMIN)
- IsSystemAdmin (User.role == ADMIN)
- CanSignDocuments (InstitutionUser.role in [ADMIN, SIGNER])

Utilise django.contrib.auth.permissions.

Exemple:
```python
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType

class IsInstitutionUser:
    def has_permission(self, request, view):
        return request.user.role == 'INSTITUTION'
```
```

---

## 🎯 Phase 15: Management Commands

### Prompt 15.1: Command Create Admin

```
Contexte: Let's Check - Backend presque terminé. Frontend: frontend/ (Inertia).

Tâche: Crée management command pour créer admin.

Fichier: apps/core/management/commands/create_admin.py

Spécifications:
- Command Django standard
- Arguments: --email, --password
- Crée User avec role=ADMIN, status=ACTIVE
- Vérifie email unique

Exemple:
```python
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Crée un superuser admin'
    
    def add_arguments(self, parser):
        parser.add_argument('--email', required=True)
        parser.add_argument('--password', required=True)
    
    def handle(self, *args, **options):
        # Code création
        pass
```

Usage: python manage.py create_admin --email=admin@letscheck.cm --password=...
```

### Prompt 15.2: Command Check Expiring Keys

```
Contexte: Let's Check - Backend OK. Frontend: frontend/ (Inertia).

Tâche: Crée command pour lister clés expirant.

Fichier: apps/cryptography/management/commands/check_expiring_keys.py

Spécifications:
- Liste clés expirant dans X jours (--days=30)
- Option --notify pour envoyer emails
- Affiche: institution, fingerprint, expire_date

Exemple:
```python
class Command(BaseCommand):
    help = 'Liste clés expirant bientôt'
    
    def add_arguments(self, parser):
        parser.add_argument('--days', type=int, default=30)
        parser.add_argument('--notify', action='store_true')
    
    def handle(self, *args, **options):
        # Code listing
        pass
```

Usage: python manage.py check_expiring_keys --days=7 --notify
```

---

## 🎯 Phase 16: Tests Unitaires Backend

### Prompt 16.1: Tests Core Services

```
Contexte: Let's Check - Backend complet. Frontend: frontend/ (Inertia).

Tâche: Crée tests pour AuditService et EmailService.

Fichiers:
- apps/core/tests/test_audit_service.py
- apps/core/tests/test_email_service.py

Tests AuditService:
- test_log_login_success()
- test_log_login_failure()
- test_log_document_sign()
- test_audit_log_immutable() (ne peut pas être modifié)

Tests EmailService:
- test_send_verification_email()
- test_template_rendering()

Utilise Django TestCase.
Fixtures: User, EmailTemplate.

Exemple:
```python
from django.test import TestCase

class AuditServiceTest(TestCase):
    def setUp(self):
        # Fixtures
        pass
    
    def test_log_login_success(self):
        # Test
        pass
```
```

### Prompt 16.2: Tests Cryptography Service

```
Contexte: Let's Check - Backend terminé. Frontend: frontend/ (Inertia).

Tâche: Crée tests CryptographyService.

Fichier: apps/cryptography/tests/test_cryptography_service.py

Tests:
- test_validate_rsa_public_key()
- test_validate_ecdsa_public_key()
- test_invalid_key_format()
- test_calculate_fingerprint()
- test_verify_signature_valid()
- test_verify_signature_invalid()

Utilise clés de test (fixtures).

Exemple:
```python
class CryptographyServiceTest(TestCase):
    def setUp(self):
        # Générer clés test
        pass
    
    def test_verify_signature_valid(self):
        # Test signature valide
        pass
```
```

### Prompt 16.3: Tests Document Service

```
Contexte: Let's Check - Backend OK. Frontend: frontend/ (Inertia).

Tâche: Crée tests DocumentService.

Fichier: apps/documents/tests/test_document_service.py

Tests:
- test_register_signed_document()
- test_verify_authentic_document()
- test_verify_invalid_hash()
- test_verify_revoked_document()
- test_revoke_document()

Fixtures: Institution, CryptographicKey, SignedDocument.

Exemple:
```python
class DocumentServiceTest(TestCase):
    def setUp(self):
        self.institution = Institution.objects.create(...)
        self.key = CryptographicKey.objects.create(...)
    
    def test_verify_authentic_document(self):
        # Test vérification authentique
        pass
```
```

---

# PARTIE 2: FRONTEND REACT/INERTIA

## 🎯 Phase 17: Setup Frontend & Utilitaires

### Prompt 17.1: Types TypeScript de Base

```
Contexte: Let's Check - Frontend React/Inertia dans frontend/ts/

Tâche: Crée les types TypeScript pour les entités principales.

Fichier: frontend/ts/types/index.ts

Référence: Section "2. Modèles de Données" dans docs/letscheck_architecture.md

Types à créer:
- User (id, email, role, status, etc.)
- Institution (id, name, type, status, logo_url, etc.)
- CryptographicKey (id, fingerprint, algorithm, status, expires_at, etc.)
- SignedDocument (id, document_hash, file_type, status, institution, key, etc.)
- DocumentVerification (result, document?, certificate_url, etc.)
- VerificationResult (result, document_data, certificate_url, timestamp)

Exemple:
```typescript
export interface User {
  id: string;
  email: string;
  role: 'ADMIN' | 'INSTITUTION' | 'PUBLIC';
  status: 'PENDING' | 'ACTIVE' | 'SUSPENDED' | 'REVOKED';
  created_at: string;
}

export interface Institution {
  id: string;
  name: string;
  legal_name: string;
  type: 'PUBLIC' | 'PRIVATE' | 'UNIVERSITY' | 'GOVERNMENT' | 'INTERNATIONAL';
  status: 'PENDING' | 'ACTIVE' | 'SUSPENDED' | 'REVOKED';
  logo_url?: string;
  country_code: string;
}

export interface VerificationResult {
  result: 'AUTHENTIC' | 'INVALID_SIGNATURE' | 'NOT_FOUND' | 'REVOKED' | 'EXPIRED' | 'KEY_EXPIRED';
  document?: {
    id: string;
    institution: Institution;
    signed_at: string;
    file_type: string;
    key_algorithm: string;
  };
  certificate_url?: string;
  verification_id: string;
  timestamp: string;
}

// ... autres types
```

Exporte tout dans types/index.ts
```

### Prompt 17.2: Service API Client

```
Contexte: Let's Check - Frontend React/Inertia.

Tâche: Crée le client API pour appels backend.

Fichier: frontend/ts/services/api.ts

Spécifications:
- Utilise axios
- Base URL: /api/
- Headers: Content-Type, CSRF token
- Intercepteurs pour erreurs
- Methods: get, post, patch, delete

Exemple:
```typescript
import axios from 'axios';

const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Intercepteur CSRF
api.interceptors.request.use((config) => {
  const csrfToken = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content');
  if (csrfToken) {
    config.headers['X-CSRFToken'] = csrfToken;
  }
  return config;
});

// Intercepteur erreurs
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error);
    return Promise.reject(error);
  }
);

export default api;
```
```

### Prompt 17.3: Hooks Custom - useToast et useDebounce

```
Contexte: Let's Check - Frontend React/Inertia.

Tâche: Crée hooks custom utiles.

Fichiers:
- frontend/ts/hooks/useToast.ts
- frontend/ts/hooks/useDebounce.ts
- frontend/ts/hooks/index.ts

useToast:
- Wrapper du toast Shadcn UI (sonner)
- Methods: success(), error(), warning(), info()

useDebounce:
- Debounce valeurs (search, etc.)
- Delay configurable

Exemple useToast:
```typescript
import { toast } from 'sonner';

export const useToast = () => {
  return {
    success: (message: string) => toast.success(message),
    error: (message: string) => toast.error(message),
    warning: (message: string) => toast.warning(message),
    info: (message: string) => toast.info(message),
  };
};
```

Exemple useDebounce:
```typescript
import { useState, useEffect } from 'react';

export function useDebounce<T>(value: T, delay: number): T {
  const [debouncedValue, setDebouncedValue] = useState<T>(value);

  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);

    return () => clearTimeout(handler);
  }, [value, delay]);

  return debouncedValue;
}
```

Exporte dans index.ts
```

---

## 🎯 Phase 18: Interface Publique - Layouts & Pages

### Prompt 18.1: Layout Public

```
Contexte: Let's Check - Frontend React/Inertia avec Shadcn UI.

Tâche: Crée le layout pour pages publiques.

Fichier: frontend/ts/components/layouts/PublicLayout.tsx

Référence: Section "3.1.1 Page d'Accueil" dans docs/letscheck_architecture.md

Composant:
- Header: Logo, Navigation (Accueil | Vérifier | FAQ | Contact), Language selector
- Footer: Liens légaux, réseaux sociaux
- Props: children, title (optionnel)

Utilise Shadcn UI:
- Button, DropdownMenu (language), Sheet (mobile menu)

Exemple structure:
```tsx
import { Button } from '@/components/ui/button';
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from '@/components/ui/dropdown-menu';
import { Link } from '@inertiajs/react';

interface PublicLayoutProps {
  children: React.ReactNode;
  title?: string;
}

export default function PublicLayout({ children, title }: PublicLayoutProps) {
  return (
    <div className="min-h-screen flex flex-col">
      <header className="border-b bg-white sticky top-0 z-50">
        <nav className="container mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center space-x-8">
            <Link href="/">
              <img src="/static/images/logo.svg" alt="Let's Check" className="h-10" />
            </Link>
            <div className="hidden md:flex space-x-4">
              <Button variant="ghost" asChild>
                <Link href="/">Accueil</Link>
              </Button>
              <Button variant="ghost" asChild>
                <Link href="/verify">Vérifier</Link>
              </Button>
              <Button variant="ghost" asChild>
                <Link href="/faq">FAQ</Link>
              </Button>
              <Button variant="ghost" asChild>
                <Link href="/contact">Contact</Link>
              </Button>
            </div>
          </div>
          
          {/* Language selector */}
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="outline" size="sm">FR</Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent>
              <DropdownMenuItem>Français</DropdownMenuItem>
              <DropdownMenuItem>English</DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </nav>
      </header>
      
      <main className="flex-1">
        {children}
      </main>
      
      <footer className="border-t bg-gray-50 mt-auto">
        <div className="container mx-auto px-4 py-8">
          <div className="grid md:grid-cols-3 gap-8">
            <div>
              <h3 className="font-semibold mb-4">Let's Check</h3>
              <p className="text-sm text-gray-600">
                Vérification d'authenticité de documents
              </p>
            </div>
            <div>
              <h3 className="font-semibold mb-4">Liens</h3>
              <ul className="space-y-2 text-sm">
                <li><Link href="/legal" className="text-gray-600 hover:text-gray-900">Mentions légales</Link></li>
                <li><Link href="/privacy" className="text-gray-600 hover:text-gray-900">Confidentialité</Link></li>
                <li><Link href="/terms" className="text-gray-600 hover:text-gray-900">CGU</Link></li>
              </ul>
            </div>
            <div>
              <h3 className="font-semibold mb-4">Contact</h3>
              <p className="text-sm text-gray-600">contact@letscheck.cm</p>
            </div>
          </div>
          <div className="mt-8 pt-8 border-t text-center text-sm text-gray-600">
            © {new Date().getFullYear()} Let's Check. Tous droits réservés.
          </div>
        </div>
      </footer>
    </div>
  );
}
```
```

### Prompt 18.2: Page d'Accueil

```
Contexte: Let's Check - Frontend React/Inertia.

Tâche: Crée la page d'accueil publique.

Fichier: frontend/ts/pages/Home.tsx

Référence: Section "3.1.1 Page d'Accueil" dans docs/letscheck_architecture.md

Structure (consulter le document):
- Hero section avec CTA "Vérifier un Document"
- Section Fonctionnalités (3 cards: Rapide, Sécurisé, Gratuit)
- Section "Comment ça marche" (timeline 3 étapes)
- Section Statistiques (compteurs animés)

Props Inertia reçues de Django:
- stats: { verifications_today, institutions_count, satisfaction_rate }

Utilise Shadcn UI:
- Button, Card, Badge

Exemple:
```tsx
import { Head, Link } from '@inertiajs/react';
import PublicLayout from '@/components/layouts/PublicLayout';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Clock, Shield, DollarSign, CheckCircle } from 'lucide-react';

interface HomeProps {
  stats: {
    verifications_today: number;
    institutions_count: number;
    satisfaction_rate: number;
  };
}

export default function Home({ stats }: HomeProps) {
  return (
    <PublicLayout>
      <Head title="Let's Check - Vérification de documents" />
      
      {/* Hero Section */}
      <section className="py-20 bg-gradient-to-b from-blue-50 to-white">
        <div className="container mx-auto px-4 text-center">
          <h1 className="text-5xl font-bold mb-6 text-gray-900">
            Vérifiez l'authenticité de vos documents en quelques secondes
          </h1>
          <p className="text-xl text-gray-600 mb-8 max-w-2xl mx-auto">
            Service gratuit, sécurisé et instantané pour valider diplômes, certificats et documents officiels
          </p>
          <Button size="lg" asChild className="text-lg px-8 py-6">
            <Link href="/verify">Vérifier un Document</Link>
          </Button>
        </div>
      </section>
      
      {/* Features Section */}
      <section className="py-16">
        <div className="container mx-auto px-4">
          <div className="grid md:grid-cols-3 gap-8">
            <Card className="text-center">
              <CardHeader>
                <Clock className="h-12 w-12 text-blue-600 mx-auto mb-4" />
                <CardTitle>Rapide</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-gray-600">Vérification en moins de 5 secondes</p>
              </CardContent>
            </Card>
            
            <Card className="text-center">
              <CardHeader>
                <Shield className="h-12 w-12 text-green-600 mx-auto mb-4" />
                <CardTitle>Sécurisé</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-gray-600">Cryptographie de niveau bancaire</p>
              </CardContent>
            </Card>
            
            <Card className="text-center">
              <CardHeader>
                <DollarSign className="h-12 w-12 text-purple-600 mx-auto mb-4" />
                <CardTitle>Gratuit</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-gray-600">Service accessible à tous sans frais</p>
              </CardContent>
            </Card>
          </div>
        </div>
      </section>
      
      {/* How it works */}
      <section className="py-16 bg-gray-50">
        <div className="container mx-auto px-4">
          <h2 className="text-3xl font-bold text-center mb-12">Comment ça marche</h2>
          <div className="max-w-3xl mx-auto space-y-8">
            <div className="flex items-start gap-4">
              <div className="flex-shrink-0 w-10 h-10 bg-blue-600 text-white rounded-full flex items-center justify-center font-bold">1</div>
              <div>
                <h3 className="font-semibold text-lg mb-2">Uploadez votre document ou scannez le QR code</h3>
                <p className="text-gray-600">Formats supportés: PDF, JPG, PNG, DOCX</p>
              </div>
            </div>
            <div className="flex items-start gap-4">
              <div className="flex-shrink-0 w-10 h-10 bg-blue-600 text-white rounded-full flex items-center justify-center font-bold">2</div>
              <div>
                <h3className="font-semibold text-lg mb-2">Notre système vérifie la signature cryptographique</h3>
                <p className="text-gray-600">Validation instantanée contre notre base de données sécurisée</p>
              </div>
            </div>
            <div className="flex items-start gap-4">
              <div className="flex-shrink-0 w-10 h-10 bg-blue-600 text-white rounded-full flex items-center justify-center font-bold">3</div>
              <div>
                <h3 className="font-semibold text-lg mb-2">Recevez instantanément le résultat avec certificat</h3>
                <p className="text-gray-600">Certificat PDF téléchargeable comme preuve de vérification</p>
              </div>
            </div>
          </div>
        </div>
      </section>
      
      {/* Stats Section */}
      <section className="py-16">
        <div className="container mx-auto px-4">
          <div className="grid md:grid-cols-3 gap-8 text-center">
            <div>
              <div className="text-5xl font-bold text-blue-600 mb-2">
                {stats.verifications_today.toLocaleString()}
              </div>
              <div className="text-gray-600">Vérifications aujourd'hui</div>
            </div>
            <div>
              <div className="text-5xl font-bold text-green-600 mb-2">
                {stats.institutions_count}
              </div>
              <div className="text-gray-600">Institutions partenaires</div>
            </div>
            <div>
              <div className="text-5xl font-bold text-purple-600 mb-2">
                {stats.satisfaction_rate}%
              </div>
              <div className="text-gray-600">Taux de satisfaction</div>
            </div>
          </div>
        </div>
      </section>
    </PublicLayout>
  );
}
```
```

---

## 🎯 Phase 19: Composants Vérification

### Prompt 19.1: Composant UploadZone

```
Contexte: Let's Check - Frontend React/Inertia avec Shadcn UI.

Tâche: Crée composant drag-and-drop pour upload documents.

Fichier: frontend/ts/components/UploadZone.tsx

Référence: Section "3.1.2 Page de Vérification - Tab 1: Upload Fichier" dans docs/letscheck_architecture.md

Props:
- onFileSelect: (file: File) => void
- acceptedTypes: string[] (default: ['application/pdf', 'image/jpeg', 'image/png'])
- maxSizeMB: number (default: 10)

Features:
- Drag and drop visuel
- Click to browse
- Validation taille et format
- Preview si image
- Affichage erreurs

Utilise Shadcn UI:
- Card, Alert

Exemple:
```tsx
import { useState } from 'react';
import { Card } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Upload, FileText } from 'lucide-react';

interface UploadZoneProps {
  onFileSelect: (file: File) => void;
  acceptedTypes?: string[];
  maxSizeMB?: number;
}

export default function UploadZone({ 
  onFileSelect, 
  acceptedTypes = ['application/pdf', 'image/jpeg', 'image/png', 'image/jpg'],
  maxSizeMB = 10 
}: UploadZoneProps) {
  const [isDragging, setIsDragging] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  
  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    
    const file = e.dataTransfer.files[0];
    validateAndSelect(file);
  };
  
  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) validateAndSelect(file);
  };
  
  const validateAndSelect = (file: File) => {
    // Validation taille
    if (file.size > maxSizeMB * 1024 * 1024) {
      setError(`Fichier trop volumineux (max ${maxSizeMB}MB)`);
      return;
    }
    
    // Validation type
    if (acceptedTypes && !acceptedTypes.includes(file.type)) {
      setError('Format de fichier non supporté');
      return;
    }
    
    // Preview si image
    if (file.type.startsWith('image/')) {
      const reader = new FileReader();
      reader.onload = (e) => setPreview(e.target?.result as string);
      reader.readAsDataURL(file);
    }
    
    setError(null);
    onFileSelect(file);
  };
  
  return (
    <div className="space-y-4">
      <Card 
        className={`p-12 border-2 border-dashed text-center cursor-pointer transition-colors ${
          isDragging ? 'border-blue-500 bg-blue-50' : 'border-gray-300 hover:border-gray-400'
        }`}
        onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
        onDragLeave={() => setIsDragging(false)}
        onDrop={handleDrop}
        onClick={() => document.getElementById('file-input')?.click()}
      >
        <Upload className="mx-auto h-12 w-12 text-gray-400 mb-4" />
        <p className="text-lg mb-2">Glissez votre document ici ou cliquez pour parcourir</p>
        <p className="text-sm text-gray-500">PDF, JPG, PNG (max {maxSizeMB}MB)</p>
        
        <input
          id="file-input"
          type="file"
          className="hidden"
          accept={acceptedTypes.join(',')}
          onChange={handleFileInput}
        />
      </Card>
      
      {error && (
        <Alert variant="destructive">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}
      
      {preview && (
        <div className="flex justify-center">
          <img src={preview} alt="Preview" className="max-h-48 rounded-lg border" />
        </div>
      )}
    </div>
  );
}
```
```

### Prompt 19.2: Hook useDocumentHash

```
Contexte: Let's Check - Frontend React/Inertia.

Tâche: Crée hook pour calculer hash SHA-256 côté client.

Fichier: frontend/ts/hooks/useDocumentHash.ts

Référence: Section "11.1 Gestion des Formats - Hash Calculation Frontend" dans docs/letscheck_architecture.md

Spécifications:
- Utilise Web Crypto API
- Calcule SHA-256
- Progress callback
- Retourne: { hash, isCalculating, error, progress, calculateHash }

Exemple:
```typescript
import { useState } from 'react';

export function useDocumentHash() {
  const [hash, setHash] = useState<string | null>(null);
  const [isCalculating, setIsCalculating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [progress, setProgress] = useState(0);

  const calculateHash = async (file: File): Promise<string> => {
    setIsCalculating(true);
    setError(null);
    setProgress(0);

    try {
      const buffer = await file.arrayBuffer();
      
      // Simulation progress (Web Crypto API est quasi-instantané)
      setProgress(50);
      
      const hashBuffer = await crypto.subtle.digest('SHA-256', buffer);
      const hashArray = Array.from(new Uint8Array(hashBuffer));
      const hashHex = hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
      
      setProgress(100);
      setHash(hashHex);
      return hashHex;
    } catch (err) {
      const errorMessage = 'Erreur lors du calcul du hash';
      setError(errorMessage);
      throw new Error(errorMessage);
    } finally {
      setIsCalculating(false);
    }
  };

  const reset = () => {
    setHash(null);
    setError(null);
    setProgress(0);
  };

  return { hash, isCalculating, error, progress, calculateHash, reset };
}
```

Mets à jour hooks/index.ts
```

### Prompt 19.3: Composant VerificationResult

```
Contexte: Let's Check - Frontend React/Inertia avec Shadcn UI.

Tâche: Crée composant d'affichage des résultats de vérification.

Fichier: frontend/ts/components/VerificationResult.tsx

Référence: Section "3.1.2 Page de Vérification - Résultat de Vérification" dans docs/letscheck_architecture.md

Props:
- result: VerificationResult (type défini dans types/index.ts)

Affichage selon result (consulter document):
- AUTHENTIC: Card verte, checkmark, infos document, boutons (certificat, historique)
- INVALID_SIGNATURE: Card rouge, X, raison
- NOT_FOUND: Card orange, warning
- REVOKED: Card rouge foncé, ban icon
- EXPIRED: Card orange, clock icon
- KEY_EXPIRED: Card orange, key icon

Utilise Shadcn UI:
- Card, Alert, Button, Badge
- Icons: Lucide (Check, X, AlertTriangle, Ban, Clock, Key)

Exemple:
```tsx
import { Card, CardContent, CardHeader } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Check, X, AlertTriangle, Ban, Clock, Key, Download, History } from 'lucide-react';
import { VerificationResult as VerificationResultType } from '@/types';

interface VerificationResultProps {
  result: VerificationResultType;
  onViewHistory?: () => void;
  onReport?: () => void;
}

export default function VerificationResult({ result, onViewHistory, onReport }: VerificationResultProps) {
  const resultConfig = {
    AUTHENTIC: {
      color: 'bg-green-50 border-green-200',
      icon: <Check className="h-16 w-16 text-green-600" />,
      title: '✓ Document Authentique',
      titleColor: 'text-green-800',
      description: 'Ce document est authentique et sa signature est valide.'
    },
    INVALID_SIGNATURE: {
      color: 'bg-red-50 border-red-200',
      icon: <X className="h-16 w-16 text-red-600" />,
      title: '✗ Document Invalide',
      titleColor: 'text-red-800',
      description: 'La signature numérique est invalide. Le document peut avoir été modifié.'
    },
    NOT_FOUND: {
      color: 'bg-orange-50 border-orange-200',
      icon: <AlertTriangle className="h-16 w-16 text-orange-600" />,
      title: '⚠ Document Non Trouvé',
      titleColor: 'text-orange-800',
      description: 'Ce document n\'est pas enregistré dans notre base de données.'
    },
    REVOKED: {
      color: 'bg-red-100 border-red-300',
      icon: <Ban className="h-16 w-16 text-red-700" />,
      title: '🚫 Document Révoqué',
      titleColor: 'text-red-900',
      description: 'Ce document a été officiellement révoqué par l\'institution émettrice.'
    },
    EXPIRED: {
      color: 'bg-orange-50 border-orange-200',
      icon: <Clock className="h-16 w-16 text-orange-600" />,
      title: '⏰ Document Expiré',
      titleColor: 'text-orange-800',
      description: 'Ce document a dépassé sa date de validité.'
    },
    KEY_EXPIRED: {
      color: 'bg-orange-50 border-orange-200',
      icon: <Key className="h-16 w-16 text-orange-600" />,
      title: '🔑 Clé Expirée',
      titleColor: 'text-orange-800',
      description: 'La clé cryptographique utilisée pour signer ce document a expiré.'
    },
  };

  const config = resultConfig[result.result];

  return (
    <Card className={`${config.color} border-2`}>
      <CardHeader>
        <div className="text-center mb-4">
          {config.icon}
          <h2 className={`text-2xl font-bold mt-4 ${config.titleColor}`}>
            {config.title}
          </h2>
          <p className="text-gray-600 mt-2">{config.description}</p>
        </div>
      </CardHeader>

      <CardContent>
        {result.result === 'AUTHENTIC' && result.document && (
          <div className="space-y-6">
            <div className="grid md:grid-cols-2 gap-4 bg-white p-4 rounded-lg">
              <div>
                <p className="text-sm text-gray-600">Institution émettrice</p>
                <div className="flex items-center gap-2 mt-1">
                  {result.document.institution.logo_url && (
                    <img src={result.document.institution.logo_url} alt="" className="h-8 w-8 rounded" />
                  )}
                  <p className="font-semibold">{result.document.institution.name}</p>
                </div>
              </div>
              <div>
                <p className="text-sm text-gray-600">Date de signature</p>
                <p className="font-semibold mt-1">
                  {new Date(result.document.signed_at).toLocaleDateString('fr-FR', {
                    year: 'numeric',
                    month: 'long',
                    day: 'numeric'
                  })}
                </p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Type de document</p>
                <p className="font-semibold mt-1">{result.document.file_type}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Algorithme</p>
                <p className="font-semibold mt-1">{result.document.key_algorithm}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Statut</p>
                <Badge className="bg-green-600 mt-1">Valide</Badge>
              </div>
              <div>
                <p className="text-sm text-gray-600">ID Vérification</p>
                <p className="font-mono text-xs mt-1">{result.verification_id.slice(0, 8)}...</p>
              </div>
            </div>

            <div className="flex flex-col sm:flex-row gap-3">
              {result.certificate_url && (
                <Button asChild className="flex-1">
                  <a href={result.certificate_url} download>
                    <Download className="mr-2 h-4 w-4" />
                    Télécharger le Certificat
                  </a>
                </Button>
              )}
              {onViewHistory && (
                <Button variant="outline" className="flex-1" onClick={onViewHistory}>
                  <History className="mr-2 h-4 w-4" />
                  Voir l'historique
                </Button>
              )}
            </div>
          </div>
        )}

        {result.result === 'INVALID_SIGNATURE' && (
          <Alert variant="destructive">
            <AlertDescription>
              La signature numérique de ce document est invalide. Le document a peut-être été modifié après signature ou la signature est corrompue.
            </AlertDescription>
          </Alert>
        )}

        {result.result === 'NOT_FOUND' && (
          <div className="space-y-4">
            <Alert>
              <AlertDescription>
                <ul className="list-disc list-inside space-y-1">
                  <li>L'institution émettrice n'utilise pas Let's Check</li>
                  <li>Le document est peut-être ancien (pré-2024)</li>
                  <li>Le document n'a pas été enregistré correctement</li>
                </ul>
              </AlertDescription>
            </Alert>
            {onReport && (
              <Button variant="outline" onClick={onReport} className="w-full">
                <AlertTriangle className="mr-2 h-4 w-4" />
                Signaler comme Suspect
              </Button>
            )}
          </div>
        )}

        {result.result === 'REVOKED' && (
          <Alert variant="destructive">
            <AlertDescription>
              <strong>AVERTISSEMENT:</strong> N'acceptez PAS ce document comme valide. Il a été officiellement révoqué par l'institution émettrice.
            </AlertDescription>
          </Alert>
        )}

        {(result.result === 'EXPIRED' || result.result === 'KEY_EXPIRED') && (
          <Alert>
            <AlertDescription>
              Ce document n'est plus valide. Contactez l'institution émettrice pour obtenir une version mise à jour.
            </AlertDescription>
          </Alert>
        )}

        {result.result !== 'AUTHENTIC' && onReport && (
          <div className="mt-4 pt-4 border-t">
            <Button variant="ghost" onClick={onReport} className="w-full">
              Signaler un Problème
            </Button>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
```
```

### Prompt 19.4: Page Vérification

```
Contexte: Let's Check - Frontend React/Inertia avec Shadcn UI.

Tâche: Crée la page de vérification avec tabs (Upload, QR, Hash manuel).

Fichier: frontend/ts/pages/Verify.tsx

Référence: Section "3.1.2 Page de Vérification" dans docs/letscheck_architecture.md

Structure:
- Tabs Shadcn UI (3 tabs)
- Tab 1: UploadZone component
- Tab 2: QR Scanner (placeholder avec message)
- Tab 3: Input hash manuel
- Résultat affiché en dessous (VerificationResult)

Flow:
1. User upload/scan/entre hash
2. Calcul hash si upload (useDocumentHash)
3. POST /api/public/verify avec hash
4. Affichage résultat

Utilise Shadcn UI:
- Tabs, Card, Button, Input, Progress

Exemple:
```tsx
import { useState } from 'react';
import { Head } from '@inertiajs/react';
import PublicLayout from '@/components/layouts/PublicLayout';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Progress } from '@/components/ui/progress';
import UploadZone from '@/components/UploadZone';
import VerificationResult from '@/components/VerificationResult';
import { useDocumentHash } from '@/hooks/useDocumentHash';
import { useToast } from '@/hooks/useToast';
import api from '@/services/api';
import { VerificationResult as VerificationResultType } from '@/types';

export default function Verify() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [manualHash, setManualHash] = useState('');
  const [verificationResult, setVerificationResult] = useState<VerificationResultType | null>(null);
  const [isVerifying, setIsVerifying] = useState(false);
  
  const { hash, isCalculating, progress, calculateHash, reset } = useDocumentHash();
  const toast = useToast();

  const handleFileSelect = async (file: File) => {
    setSelectedFile(file);
    setVerificationResult(null);
    reset();
    
    try {
      await calculateHash(file);
      toast.success('Hash calculé avec succès');
    } catch (error) {
      toast.error('Erreur lors du calcul du hash');
    }
  };

  const handleVerify = async (documentHash: string) => {
    setIsVerifying(true);
    try {
      const response = await api.post('/public/verify', {
        document_hash: documentHash,
        method: 'UPLOAD'
      });
      setVerificationResult(response.data);
    } catch (error) {
      toast.error('Erreur lors de la vérification');
      console.error('Verification error:', error);
    } finally {
      setIsVerifying(false);
    }
  };

  const isHashValid = (h: string) => /^[a-f0-9]{64}$/i.test(h);

  return (
    <PublicLayout>
      <Head title="Vérifier un document - Let's Check" />
      
      <div className="container mx-auto px-4 py-12 max-w-4xl">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold mb-4">Vérifier l'authenticité d'un document</h1>
          <p className="text-gray-600">Uploadez votre document, scannez le QR code ou entrez le hash manuellement</p>
        </div>
        
        <Card className="p-6">
          <Tabs defaultValue="upload" className="w-full">
            <TabsList className="grid w-full grid-cols-3 mb-6">
              <TabsTrigger value="upload">Upload Fichier</TabsTrigger>
              <TabsTrigger value="qr">Scanner QR Code</TabsTrigger>
              <TabsTrigger value="hash">Hash Manuel</TabsTrigger>
            </TabsList>
            
            <TabsContent value="upload" className="space-y-4">
              <UploadZone onFileSelect={handleFileSelect} />
              
              {isCalculating && (
                <div className="space-y-2">
                  <p className="text-center text-sm text-gray-600">Calcul du hash en cours...</p>
                  <Progress value={progress} className="w-full" />
                </div>
              )}
              
              {hash && (
                <div className="space-y-4">
                  <div className="p-4 bg-gray-50 rounded-lg">
                    <p className="text-sm text-gray-600 mb-2">Hash SHA-256:</p>
                    <p className="font-mono text-xs break-all">{hash}</p>
                  </div>
                  <Button 
                    onClick={() => handleVerify(hash)} 
                    disabled={isVerifying}
                    className="w-full"
                    size="lg"
                  >
                    {isVerifying ? 'Vérification en cours...' : 'Vérifier le Document'}
                  </Button>
                </div>
              )}
            </TabsContent>
            
            <TabsContent value="qr">
              <Card className="p-12 text-center">
                <div className="text-gray-500">
                  <p className="text-lg mb-4">Scanner QR Code</p>
                  <p className="text-sm">Fonctionnalité à venir</p>
                  <p className="text-xs mt-2">Cette fonctionnalité permettra de scanner directement le QR code présent sur vos documents.</p>
                </div>
              </Card>
            </TabsContent>
            
            <TabsContent value="hash" className="space-y-4">
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium mb-2">Hash SHA-256 du document</label>
                  <Input
                    placeholder="Entrez le hash (64 caractères hexadécimaux)"
                    value={manualHash}
                    onChange={(e) => setManualHash(e.target.value.toLowerCase())}
                    maxLength={64}
                    className="font-mono"
                  />
                  <p className="text-xs text-gray-500 mt-2">
                    Le hash se trouve généralement au bas du document ou dans les métadonnées
                  </p>
                </div>
                <Button 
                  onClick={() => handleVerify(manualHash)} 
                  disabled={isVerifying || !isHashValid(manualHash)}
                  className="w-full"
                  size="lg"
                >
                  {isVerifying ? 'Vérification en cours...' : 'Vérifier le Document'}
                </Button>
              </div>
            </TabsContent>
          </Tabs>
        </Card>
        
        {verificationResult && (
          <div className="mt-8 animate-in slide-in-from-bottom duration-500">
            <VerificationResult 
              result={verificationResult}
              onViewHistory={() => {/* TODO */}}
              onReport={() => {/* TODO */}}
            />
          </div>
        )}
      </div>
    </PublicLayout>
  );
}
```
```

---

## 🎯 Phase 20: Dashboard Admin - Layout & Pages

### Prompt 20.1: Layout Admin

```
Contexte: Let's Check - Frontend React/Inertia avec Shadcn UI.

Tâche: Crée le layout pour dashboard admin.

Fichier: frontend/ts/components/layouts/AdminLayout.tsx

Référence: Section "3.2.1 Dashboard Administrateur" dans docs/letscheck_architecture.md

Composant:
- Sidebar avec navigation (consulter document pour liste complète)
- Header avec user dropdown
- Content area responsive

Sidebar items:
- 📊 Tableau de Bord
- 🏢 Institutions
- 🔑 Clés Cryptographiques
- 📄 Documents
- 🚨 Signalements
- 👥 Utilisateurs
- 📈 Statistiques
- 📋 Logs d'Audit
- ⚙️ Paramètres

Props:
- children
- user: User (pour dropdown)

Utilise Shadcn UI:
- Sheet (mobile sidebar), DropdownMenu (user), Button, ScrollArea

Exemple:
```tsx
import { useState } from 'react';
import { Link } from '@inertiajs/react';
import { Button } from '@/components/ui/button';
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from '@/components/ui/dropdown-menu';
import { Sheet, SheetContent, SheetTrigger } from '@/components/ui/sheet';
import { ScrollArea } from '@/components/ui/scroll-area';
import { 
  LayoutDashboard, 
  Building2, 
  Key, 
  FileText, 
  AlertTriangle, 
  Users, 
  BarChart3, 
  ScrollText, 
  Settings, 
  LogOut,
  Menu,
  ChevronDown
} from 'lucide-react';
import { User } from '@/types';

interface AdminLayoutProps {
  children: React.ReactNode;
  user: User;
}

export default function AdminLayout({ children, user }: AdminLayoutProps) {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  
  const menuItems = [
    { icon: LayoutDashboard, label: 'Tableau de Bord', href: '/admin/dashboard' },
    { icon: Building2, label: 'Institutions', href: '/admin/institutions' },
    { icon: Key, label: 'Clés Cryptographiques', href: '/admin/keys' },
    { icon: FileText, label: 'Documents', href: '/admin/documents' },
    { icon: AlertTriangle, label: 'Signalements', href: '/admin/reports' },
    { icon: Users, label: 'Utilisateurs', href: '/admin/users' },
    { icon: BarChart3, label: 'Statistiques', href: '/admin/analytics' },
    { icon: ScrollText, label: 'Logs d\'Audit', href: '/admin/audit' },
    { icon: Settings, label: 'Paramètres', href: '/admin/settings' },
  ];

  const Sidebar = () => (
    <div className="h-full flex flex-col">
      <div className="p-6 border-b">
        <img src="/static/images/logo.svg" alt="Let's Check" className="h-8 mb-2" />
        <p className="text-xs font-semibold text-gray-500">ADMIN PANEL</p>
      </div>
      
      <ScrollArea className="flex-1 px-4 py-4">
        <nav className="space-y-1">
          {menuItems.map((item) => {
            const Icon = item.icon;
            const isActive = window.location.pathname === item.href;
            
            return (
              <Link key={item.href} href={item.href}>
                <Button 
                  variant={isActive ? "secondary" : "ghost"} 
                  className="w-full justify-start"
                >
                  <Icon className="mr-3 h-4 w-4" />
                  {item.label}
                </Button>
              </Link>
            );
          })}
        </nav>
      </ScrollArea>
      
      <div className="p-4 border-t mt-auto">
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="outline" className="w-full justify-between">
              <span className="truncate">{user.email}</span>
              <ChevronDown className="ml-2 h-4 w-4" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="start" className="w-56">
            <DropdownMenuItem asChild>
              <Link href="/admin/profile">Profil</Link>
            </DropdownMenuItem>
            <DropdownMenuItem asChild>
              <Link href="/logout" method="post">
                <LogOut className="mr-2 h-4 w-4" />
                Déconnexion
              </Link>
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    </div>
  );

  return (
    <div className="flex h-screen bg-gray-100">
      {/* Desktop Sidebar */}
      <aside className="w-64 bg-white border-r hidden md:block">
        <Sidebar />
      </aside>
      
      {/* Mobile Sidebar */}
      <Sheet open={sidebarOpen} onOpenChange={setSidebarOpen}>
        <SheetContent side="left" className="p-0 w-64">
          <Sidebar />
        </SheetContent>
      </Sheet>
      
      {/* Main Content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Mobile Header */}
        <header className="md:hidden bg-white border-b p-4 flex items-center justify-between">
          <Sheet>
            <SheetTrigger asChild>
              <Button variant="ghost" size="icon">
                <Menu className="h-6 w-6" />
              </Button>
            </SheetTrigger>
          </Sheet>
          <img src="/static/images/logo.svg" alt="Let's Check" className="h-8" />
          <div className="w-10" /> {/* Spacer */}
        </header>
        
        {/* Content */}
        <main className="flex-1 overflow-auto">
          {children}
        </main>
      </div>
    </div>
  );
}
```
```

### Prompt 20.2: Page Dashboard Admin

```
Contexte: Let's Check - Frontend React/Inertia avec Shadcn UI.

Tâche: Crée le dashboard administrateur.

Fichier: frontend/ts/pages/admin/Dashboard.tsx

Référence: Section "3.2.1 Dashboard Administrateur - Contenu Principal" dans docs/letscheck_architecture.md

Props Inertia de Django:
- user: User
- metrics: { institutions_active, verifications_today, pending_reports, expiring_keys }
- chartData: { dates, success, failed }
- alerts: [ { type, message, link } ]
- recentActivity: [ { action, timestamp, user_name } ]

Sections (consulter document):
1. Métriques clés (4 cards)
2. Graphiques (verifications 30j)
3. Alertes & Actions requises
4. Activité récente

Utilise Shadcn UI:
- Card, Badge, Alert, Button
- recharts pour graphiques

Exemple:
```tsx
import { Head, Link } from '@inertiajs/react';
import AdminLayout from '@/components/layouts/AdminLayout';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Button } from '@/components/ui/button';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import { TrendingUp, Building2, AlertTriangle, Key } from 'lucide-react';
import { User } from '@/types';

interface DashboardProps {
  user: User;
  metrics: {
    institutions_active: number;
    verifications_today: number;
    pending_reports: number;
    expiring_keys: number;
  };
  chartData: {
    dates: string[];
    success: number[];
    failed: number[];
  };
  alerts: Array<{
    type: 'info' | 'warning' | 'error';
    message: string;
    link: string;
  }>;
  recentActivity: Array<{
    action: string;
    timestamp: string;
    user_name: string;
  }>;
}

export default function Dashboard({ user, metrics, chartData, alerts, recentActivity }: DashboardProps) {
  // Transform data for recharts
  const chartFormattedData = chartData.dates.map((date, i) => ({
    date,
    success: chartData.success[i],
    failed: chartData.failed[i],
    total: chartData.success[i] + chartData.failed[i]
  }));

  return (
    <AdminLayout user={user}>
      <Head title="Dashboard Admin - Let's Check" />
      
      <div className="p-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold">Tableau de Bord</h1>
          <p className="text-gray-600">Vue d'ensemble de la plateforme</p>
        </div>
        
        {/* Métriques Clés */}
        <div className="grid md:grid-cols-4 gap-6 mb-8">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium">Institutions Actives</CardTitle>
              <Building2 className="h-4 w-4 text-gray-500" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{metrics.institutions_active}</div>
              <p className="text-xs text-gray-500 mt-1">Institutions vérifiées</p>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium">Vérifications Aujourd'hui</CardTitle>
              <TrendingUp className="h-4 w-4 text-gray-500" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{metrics.verifications_today.toLocaleString()}</div>
              <p className="text-xs text-gray-500 mt-1">Depuis minuit</p>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium">Signalements Pending</CardTitle>
              <AlertTriangle className={`h-4 w-4 ${metrics.pending_reports > 0 ? 'text-red-500' : 'text-gray-500'}`} />
            </CardHeader>
            <CardContent>
              <div className={`text-2xl font-bold ${metrics.pending_reports > 0 ? 'text-red-600' : ''}`}>
                {metrics.pending_reports}
              </div>
              <p className="text-xs text-gray-500 mt-1">À traiter</p>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium">Clés Expirant &lt;30j</CardTitle>
              <Key className={`h-4 w-4 ${metrics.expiring_keys > 0 ? 'text-orange-500' : 'text-gray-500'}`} />
            </CardHeader>
            <CardContent>
              <div className={`text-2xl font-bold ${metrics.expiring_keys > 0 ? 'text-orange-600' : ''}`}>
                {metrics.expiring_keys}
              </div>
              <p className="text-xs text-gray-500 mt-1">Nécessitent rotation</p>
            </CardContent>
          </Card>
        </div>
        
        {/* Graphique Vérifications */}
        <div className="grid md:grid-cols-1 gap-6 mb-8">
          <Card>
            <CardHeader>
              <CardTitle>Vérifications sur 30 jours</CardTitle>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={chartFormattedData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis 
                    dataKey="date" 
                    tick={{ fontSize: 12 }}
                    angle={-45}
                    textAnchor="end"
                    height={60}
                  />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Line 
                    type="monotone" 
                    dataKey="success" 
                    stroke="#22c55e" 
                    strokeWidth={2}
                    name="Succès" 
                  />
                  <Line 
                    type="monotone" 
                    dataKey="failed" 
                    stroke="#ef4444" 
                    strokeWidth={2}
                    name="Échecs" 
                  />
                  <Line 
                    type="monotone" 
                    dataKey="total" 
                    stroke="#3b82f6" 
                    strokeWidth={2}
                    name="Total" 
                    strokeDasharray="5 5"
                  />
                </LineChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </div>
        
        {/* Alertes */}
        <Card className="mb-8">
          <CardHeader>
            <CardTitle>Alertes & Actions Requises</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {alerts.length === 0 ? (
              <p className="text-gray-500 text-center py-4">Aucune alerte pour le moment</p>
            ) : (
              alerts.map((alert, i) => (
                <Alert key={i} variant={alert.type === 'error' ? 'destructive' : 'default'}>
                  <AlertDescription className="flex items-center justify-between">
                    <span>{alert.message}</span>
                    <Button variant="link" size="sm" asChild>
                      <Link href={alert.link}>Traiter →</Link>
                    </Button>
                  </AlertDescription>
                </Alert>
              ))
            )}
          </CardContent>
        </Card>
        
        {/* Activité Récente */}
        <Card>
          <CardHeader>
            <CardTitle>Activité Récente</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {recentActivity.map((activity, i) => (
                <div key={i} className="flex items-start gap-4 pb-4 border-b last:border-0 last:pb-0">
                  <div className="w-2 h-2 bg-blue-500 rounded-full mt-2" />
                  <div className="flex-1">
                    <p className="text-sm">{activity.action}</p>
                    <p className="text-xs text-gray-500 mt-1">
                      {activity.user_name} • {new Date(activity.timestamp).toLocaleString('fr-FR')}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </AdminLayout>
  );
}
```
```

### Prompt 20.3: Page Gestion Institutions

```
Contexte: Let's Check - Frontend React/Inertia avec Shadcn UI.

Tâche: Crée page de gestion des institutions (liste + filtres).

Fichier: frontend/ts/pages/admin/Institutions.tsx

Référence: Section "3.2.2 Gestion des Institutions" dans docs/letscheck_architecture.md

Props Inertia:
- user: User
- institutions: Institution[]
- filters: { status?, type?, search? }

Features (consulter document):
- Filtres: status, type, search
- Table: logo, nom, type, pays, status, date inscription, actions
- Actions dropdown: Détails, Valider, Suspendre
- Pagination (via Inertia)

Utilise Shadcn UI:
- Table, Select, Input, Button, Badge, DropdownMenu

Exemple:
```tsx
import { useState } from 'react';
import { Head, Link, router } from '@inertiajs/react';
import AdminLayout from '@/components/layouts/AdminLayout';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from '@/components/ui/dropdown-menu';
import { MoreVertical, Search } from 'lucide-react';
import { User, Institution } from '@/types';

interface InstitutionsProps {
  user: User;
  institutions: Institution[];
  filters: {
    status?: string;
    type?: string;
    search?: string;
  };
}

export default function Institutions({ user, institutions, filters }: InstitutionsProps) {
  const [search, setSearch] = useState(filters.search || '');
  const [statusFilter, setStatusFilter] = useState(filters.status || 'ALL');
  const [typeFilter, setTypeFilter] = useState(filters.type || 'ALL');
  
  const handleFilter = () => {
    router.get('/admin/institutions', {
      status: statusFilter !== 'ALL' ? statusFilter : undefined,
      type: typeFilter !== 'ALL' ? typeFilter : undefined,
      search: search || undefined
    }, {
      preserveState: true,
      preserveScroll: true
    });
  };

  const getStatusBadgeClass = (status: string) => {
    switch (status) {
      case 'ACTIVE': return 'bg-green-600';
      case 'PENDING': return 'bg-yellow-600';
      case 'SUSPENDED': return 'bg-orange-600';
      case 'REVOKED': return 'bg-red-600';
      default: return 'bg-gray-600';
    }
  };

  return (
    <AdminLayout user={user}>
      <Head title="Gestion des Institutions - Admin" />
      
      <div className="p-8">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold">Institutions</h1>
            <p className="text-gray-600">Gestion et validation des institutions</p>
          </div>
        </div>
        
        {/* Filtres */}
        <div className="flex flex-wrap gap-4 mb-6">
          <Select value={statusFilter} onValueChange={setStatusFilter}>
            <SelectTrigger className="w-[200px]">
              <SelectValue placeholder="Statut" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="ALL">Tous les statuts</SelectItem>
              <SelectItem value="PENDING">En attente</SelectItem>
              <SelectItem value="ACTIVE">Active</SelectItem>
              <SelectItem value="SUSPENDED">Suspendue</SelectItem>
              <SelectItem value="REVOKED">Révoquée</SelectItem>
            </SelectContent>
          </Select>
          
          <Select value={typeFilter} onValueChange={setTypeFilter}>
            <SelectTrigger className="w-[200px]">
              <SelectValue placeholder="Type" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="ALL">Tous les types</SelectItem>
              <SelectItem value="PUBLIC">Publique</SelectItem>
              <SelectItem value="PRIVATE">Privée</SelectItem>
              <SelectItem value="UNIVERSITY">Université</SelectItem>
              <SelectItem value="GOVERNMENT">Gouvernement</SelectItem>
              <SelectItem value="INTERNATIONAL">Internationale</SelectItem>
            </SelectContent>
          </Select>
          
          <div className="flex-1 flex gap-2">
            <div className="relative flex-1 max-w-sm">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
              <Input 
                placeholder="Rechercher par nom..." 
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="pl-10"
                onKeyDown={(e) => e.key === 'Enter' && handleFilter()}
              />
            </div>
            <Button onClick={handleFilter}>Filtrer</Button>
          </div>
        </div>
        
        {/* Table */}
        <div className="bg-white rounded-lg border">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead className="w-16">Logo</TableHead>
                <TableHead>Nom</TableHead>
                <TableHead>Type</TableHead>
                <TableHead>Pays</TableHead>
                <TableHead>Statut</TableHead>
                <TableHead>Inscription</TableHead>
                <TableHead className="text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {institutions.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={7} className="text-center py-8 text-gray-500">
                    Aucune institution trouvée
                  </TableCell>
                </TableRow>
              ) : (
                institutions.map((institution) => (
                  <TableRow key={institution.id}>
                    <TableCell>
                      {institution.logo_url ? (
                        <img src={institution.logo_url} alt="" className="h-10 w-10 rounded object-cover" />
                      ) : (
                        <div className="h-10 w-10 rounded bg-gray-200 flex items-center justify-center">
                          <span className="text-xs font-semibold text-gray-500">
                            {institution.name.charAt(0)}
                          </span>
                        </div>
                      )}
                    </TableCell>
                    <TableCell>
                      <Link 
                        href={`/admin/institutions/${institution.id}`} 
                        className="font-medium hover:underline"
                      >
                        {institution.name}
                      </Link>
                      <p className="text-xs text-gray-500">{institution.legal_name}</p>
                    </TableCell>
                    <TableCell>
                      <Badge variant="outline">{institution.type}</Badge>
                    </TableCell>
                    <TableCell>
                      <span className="text-sm">{institution.country_code}</span>
                    </TableCell>
                    <TableCell>
                      <Badge className={getStatusBadgeClass(institution.status)}>
                        {institution.status}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <span className="text-sm">
                        {new Date(institution.created_at).toLocaleDateString('fr-FR')}
                      </span>
                    </TableCell>
                    <TableCell className="text-right">
                      <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                          <Button variant="ghost" size="sm">
                            <MoreVertical className="h-4 w-4"/>
                          </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="end">
                          <DropdownMenuItem asChild>
                            <Link href={`/admin/institutions/${institution.id}`}>
                              Voir détails
                            </Link>
                          </DropdownMenuItem>
                          {institution.status === 'PENDING' && (
                            <DropdownMenuItem>Valider</DropdownMenuItem>
                          )}
                          {institution.status === 'ACTIVE' && (
                            <DropdownMenuItem>Suspendre</DropdownMenuItem>
                          )}
                          {institution.status === 'SUSPENDED' && (
                            <DropdownMenuItem>Réactiver</DropdownMenuItem>
                          )}
                        </DropdownMenuContent>
                      </DropdownMenu>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </div>
      </div>
    </AdminLayout>
  );
}
```
```

---

## 📊 Checklist Complète de Progression

### Backend Django ✅

**Phase 1-2: Core**
- [ ] 1.1 User model
- [ ] 1.2 AuditLog model
- [ ] 1.3 EmailTemplate model
- [ ] 2.1 AuditService
- [ ] 2.2 EmailService
- [ ] 2.3 Tâche Huey emails

**Phase 3-4: Institutions**
- [ ] 3.1 Institution model
- [ ] 3.2 InstitutionUser model
- [ ] 4.1 InstitutionService

**Phase 5-6: Cryptography**
- [ ] 5.1 CryptographicKey model
- [ ] 5.2 KeyRotation model
- [ ] 6.1 CryptographyService
- [ ] 6.2 Tâche Huey monitoring

**Phase 7-8: Documents**
- [ ] 7.1 SignedDocument model
- [ ] 7.2 DocumentVerification model
- [ ] 8.1 DocumentService
- [ ] 8.2 CertificateService

**Phase 9-10: Verifications**
- [ ] 9.1 VerificationRequest + SuspiciousReport models
- [ ] 10.1 VerificationService

**Phase 11-12: Analytics**
- [ ] 11.1 Statistic + PerformanceMetric models
- [ ] 12.1 AnalyticsService
- [ ] 12.2 Tâche Huey aggregation

**Phase 13: APIs Ninja**
- [ ] 13.1 Schemas base
- [ ] 13.2 Schemas documents
- [ ] 13.3 Router institutions
- [ ] 13.4 Router keys
- [ ] 13.5 Router documents
- [ ] 13.6 Router public verify
- [ ] 13.7 API principale

**Phase 14-15: Infrastructure**
- [ ] 14.1 Middleware rate limiting
- [ ] 14.2 Permissions custom
- [ ] 15.1 Command create_admin
- [ ] 15.2 Command check_expiring_keys

**Phase 16: Tests**
- [ ] 16.1 Tests core services
- [ ] 16.2 Tests cryptography service
- [ ] 16.3 Tests document service

---

### Frontend React/Inertia ✅

**Phase 17: Setup**
- [ ] 17.1 Types TypeScript
- [ ] 17.2 Service API client
- [ ] 17.3 Hooks useToast + useDebounce

**Phase 18: Interface Publique**
- [ ] 18.1 Layout public
- [ ] 18.2 Page accueil

**Phase 19: Vérification**
- [ ] 19.1 Composant UploadZone
- [ ] 19.2 Hook useDocumentHash
- [ ] 19.3 Composant VerificationResult
- [ ] 19.4 Page Verify

**Phase 20: Dashboard Admin**
- [ ] 20.1 Layout admin
- [ ] 20.2 Page dashboard
- [ ] 20.3 Page institutions

---

## 🎯 Phases Restantes à Documenter

**Phase 21: Pages Admin Supplémentaires**
- Page Détail Institution
- Page Gestion Clés
- Page Signalements (Kanban)
- Page Logs Audit

**Phase 22: Composants Avancés**
- Composant DataTable réutilisable
- Composant Modal Signalement
- Composant FilePreview
- Composant Pagination

**Phase 23: Services Frontend**
- InstitutionService (API calls)
- DocumentService
- AnalyticsService

**Phase 24: Tests Frontend**
- Tests composants (Vitest)
- Tests E2E (Playwright)

---

## 🔧 Validation après Chaque Phase

Après chaque prompt, exécute:

```bash
# Backend
python manage.py makemigrations
python manage.py migrate
python manage.py check
pytest apps/<nom_app>/tests/
flake8 apps/<nom_app>/
black apps/<nom_app>/

# Frontend
cd frontend
npm run type-check
npm run lint
npm run build
```

---

## 📝 Notes Importantes

- ⚠️ **Référence obligatoire**: `docs/letscheck_architecture.md`
- ⚠️ **Frontend séparé**: `frontend/` avec Inertia
- ⚠️ **APIs = desktop + public verify**
- ✅ **Tâches courtes**: 1 modèle/service/page par prompt
- ✅ **Shadcn UI**: Pour tous composants UI
- ✅ **TypeScript**: Strict mode
- ✅ **Tests**: Coverage 80%+

---

**Document créé le**: 2024-12-14  
**Version**: 1.0.0  
**Auteur**: Architecture Team Let's Check