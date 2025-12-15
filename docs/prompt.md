# Prompt pour Agent AI - Développement Application Let's Check

## 🎯 Mission Principale

Tu es un développeur senior chargé de développer **l'interface publique** et **l'API Django Ninja** de l'application **Let's Check**, un système de vérification d'authenticité de documents numériques basé sur la cryptographie.

## 📋 Contexte du Projet

### Architecture Existante
- **Backend**: Django 5.x avec structure modulaire (apps séparées)
- **Frontend**: React 18+ avec Inertia.js (pas de REST API classique)
- **Styling**: Tailwind CSS + Shadcn UI
- **Base de données**: PostgreSQL 15+
- **API**: Django Ninja pour endpoints publics

### Configuration Déjà en Place
✅ Logging configuré
✅ Background tasks (Huey/Celery) configurés
✅ Service email opérationnel
✅ Templates email dans `templates/email/`
✅ Variables d'environnement dans `.env.example`
✅ Toutes les apps Django créées
✅ Structure frontend initialisée

## 📁 Structure du Projet

```
letscheck_web/
├── apps/
│   ├── core/              # Auth, audit, utils
│   ├── institutions/      # Gestion institutions
│   ├── cryptography/      # Clés cryptographiques
│   ├── documents/         # Documents signés
│   ├── verifications/     # Vérifications publiques
│   └── analytics/         # Statistiques
├── frontend/
│   ├── main.css          # Styles Tailwind générés
│   └── ts/
│       ├── components/   # Composants réutilisables
│       │   └── ui/       # Shadcn UI components
│       ├── pages/        # Pages Inertia
│       ├── lib/          # Utilitaires
│       └── main.tsx      # Entry point
├── templates/
│   ├── inertia_base.html # Base Inertia
│   └── email/           # Templates email
├── config/                    # Settings Django
│   ├── settings/
│   │   ├── base.py
│   │   ├── development.py
│   │   ├── production.py
│   └── urls.py
├── manage.py
└── docs/
    ├── prompt.md          # Prompt pour Agent AI
    └── letscheck_architecture.md # Architecture de Let's Check
```

## 🎯 Objectifs de Développement

### Phase 1: API Django Ninja (Backend)

Créer une API REST complète dans `apps/verifications/api.py` avec les endpoints suivants :

#### 1. Endpoints de Vérification
```python
# POST /api/v1/verify/upload
# - Upload document + calcul hash
# - Retourne résultat vérification

# POST /api/v1/verify/hash
# - Vérification par hash direct
# - Retourne résultat + métadonnées

# GET /api/v1/verify/{hash}
# - Récupère infos document par hash
# - Retourne statut + institution

# GET /api/v1/verify/{document_id}/certificate
# - Génère certificat PDF
# - Retourne URL de téléchargement
```

#### 2. Endpoints de Signalement
```python
# POST /api/v1/reports
# - Créer signalement de document suspect
# - Validation + notification admin

# GET /api/v1/reports/{report_id}
# - Statut d'un signalement
```

#### 3. Endpoints Publics (Info)
```python
# GET /api/v1/institutions
# - Liste institutions actives
# - Pagination + filtres

# GET /api/v1/institutions/{slug}
# - Détails institution publique

# GET /api/v1/stats/public
# - Statistiques publiques
# - Nb vérifications, institutions, etc.
```

### Phase 2: Interface Publique (Frontend React + Inertia)

Développer les pages suivantes dans `frontend/ts/pages/` :

#### 1. Page d'Accueil (`Home.tsx`)
- Hero section avec CTA
- Section fonctionnalités (3 colonnes)
- Comment ça marche (timeline)
- Statistiques en temps réel
- Footer complet

#### 2. Page de Vérification (`Verify.tsx`)
- Tabs pour 3 méthodes :
  - Upload fichier (drag & drop)
  - Scan QR code (webcam)
  - Saisie hash manuel
- Affichage résultat dynamique :
  - Carte verte (authentique)
  - Carte rouge (invalide)
  - Carte orange (non trouvé)
  - Carte rouge foncé (révoqué)
- Historique des vérifications
- Bouton signalement

#### 3. Page FAQ (`FAQ.tsx`)
- Accordion avec catégories
- Barre de recherche
- Questions fréquentes

#### 4. Composants Réutilisables
```
components/
├── layout/
│   ├── Header.tsx          # Navigation principale
│   ├── Footer.tsx          # Footer avec liens
│   └── Layout.tsx          # Wrapper global
├── verification/
│   ├── UploadZone.tsx      # Zone drag-drop
│   ├── QRScanner.tsx       # Scanner QR code
│   ├── HashInput.tsx       # Input hash manuel
│   ├── ResultCard.tsx      # Affichage résultat
│   └── VerificationHistory.tsx
├── reports/
│   └── ReportModal.tsx     # Modal signalement
└── ui/                     # Shadcn components
    ├── button.tsx
    ├── card.tsx
    ├── tabs.tsx
    ├── alert.tsx
    └── ...
```

## 🔧 Spécifications Techniques

### Backend (Django Ninja)

#### Configuration API
```python
# apps/verifications/api.py
from ninja import NinjaAPI, Schema
from ninja.errors import HttpError
from django.core.files.uploadedfile import UploadedFile
import hashlib

api = NinjaAPI(
    title="Let's Check API",
    version="1.0.0",
    description="API publique de vérification de documents"
)

# Rate limiting
from django.core.cache import cache
def rate_limit(ip: str, limit: int = 10, window: int = 60):
    key = f"ratelimit:{ip}"
    count = cache.get(key, 0)
    if count >= limit:
        raise HttpError(429, "Rate limit exceeded")
    cache.set(key, count + 1, window)
```

#### Schémas Pydantic
```python
from ninja import Schema
from datetime import datetime
from typing import Optional, List

class VerifyUploadSchema(Schema):
    method: str = "UPLOAD"

class VerifyHashSchema(Schema):
    document_hash: str
    method: str = "HASH_INPUT"

class VerificationResultSchema(Schema):
    result: str  # AUTHENTIC, INVALID_SIGNATURE, NOT_FOUND, REVOKED
    document: Optional['DocumentInfoSchema'] = None
    certificate_url: Optional[str] = None
    verification_id: str

class DocumentInfoSchema(Schema):
    institution: 'InstitutionSchema'
    signed_at: datetime
    file_type: str
    key_algorithm: str
    status: str

class InstitutionSchema(Schema):
    name: str
    logo_url: Optional[str]
    country_code: str
    type: str

class ReportCreateSchema(Schema):
    document_hash: str
    report_type: str  # FAKE, ALTERED, UNAUTHORIZED, OTHER
    reason: str
    reporter_email: Optional[str] = None
    reporter_name: Optional[str] = None
```

#### Logique de Vérification
```python
# apps/verifications/services.py
from apps.documents.models import SignedDocument
from apps.core.models import AuditLog
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization
import base64

class VerificationService:
    @staticmethod
    def calculate_hash(file: UploadedFile) -> str:
        """Calcule SHA-256 du fichier"""
        hasher = hashlib.sha256()
        for chunk in file.chunks():
            hasher.update(chunk)
        return hasher.hexdigest()
    
    @staticmethod
    def verify_document(document_hash: str, ip_address: str) -> dict:
        """Vérifie l'authenticité d'un document"""
        try:
            document = SignedDocument.objects.select_related(
                'institution', 'key'
            ).get(document_hash=document_hash)
        except SignedDocument.DoesNotExist:
            return {"result": "NOT_FOUND"}
        
        # Vérifications
        if document.status == 'REVOKED':
            return {
                "result": "REVOKED",
                "revoked_at": document.revoked_at,
                "reason": document.revocation_reason
            }
        
        if document.key.status != 'ACTIVE':
            return {"result": "KEY_EXPIRED"}
        
        # Vérification cryptographique
        try:
            public_key = serialization.load_pem_public_key(
                document.key.public_key.encode()
            )
            
            public_key.verify(
                base64.b64decode(document.signature),
                document_hash.encode(),
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            
            result = "AUTHENTIC"
        except Exception:
            result = "INVALID_SIGNATURE"
        
        # Log audit
        AuditLog.objects.create(
            action_type='VERIFY',
            resource_type='DOCUMENT',
            resource_id=document.id,
            ip_address=ip_address,
            success=(result == "AUTHENTIC")
        )
        
        return {
            "result": result,
            "document": document,
            "verification_id": str(uuid.uuid4())
        }
```

### Frontend (React + Inertia)

#### Pattern Inertia pour Vérification
```tsx
// frontend/ts/pages/Verify.tsx
import React, { useState } from 'react';
import { Head, router } from '@inertiajs/react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import UploadZone from '@/components/verification/UploadZone';
import QRScanner from '@/components/verification/QRScanner';
import HashInput from '@/components/verification/HashInput';
import ResultCard from '@/components/verification/ResultCard';

interface VerifyProps {
    result?: VerificationResult;
    errors?: Record<string, string>;
}

export default function Verify({ result, errors }: VerifyProps) {
    const [loading, setLoading] = useState(false);
    
    const handleUpload = async (file: File) => {
        setLoading(true);
        
        // Calcul hash côté client
        const hash = await calculateHash(file);
        
        // Appel API ou soumission Inertia
        router.post('/verify', {
            document_hash: hash,
            method: 'UPLOAD'
        }, {
            onSuccess: () => setLoading(false),
            onError: () => setLoading(false)
        });
    };
    
    return (
        <>
            <Head title="Vérifier un Document" />
            
            <div className="container mx-auto px-4 py-8 max-w-4xl">
                <h1 className="text-3xl font-bold text-center mb-8">
                    Vérifier l'Authenticité d'un Document
                </h1>
                
                <Tabs defaultValue="upload" className="w-full">
                    <TabsList className="grid w-full grid-cols-3">
                        <TabsTrigger value="upload">Upload Fichier</TabsTrigger>
                        <TabsTrigger value="qr">Scanner QR</TabsTrigger>
                        <TabsTrigger value="hash">Entrer Hash</TabsTrigger>
                    </TabsList>
                    
                    <TabsContent value="upload">
                        <UploadZone onUpload={handleUpload} loading={loading} />
                    </TabsContent>
                    
                    <TabsContent value="qr">
                        <QRScanner onScan={handleHashSubmit} />
                    </TabsContent>
                    
                    <TabsContent value="hash">
                        <HashInput onSubmit={handleHashSubmit} loading={loading} />
                    </TabsContent>
                </Tabs>
                
                {result && (
                    <ResultCard result={result} className="mt-8" />
                )}
            </div>
        </>
    );
}

// Utilitaire calcul hash
async function calculateHash(file: File): Promise<string> {
    const buffer = await file.arrayBuffer();
    const hashBuffer = await crypto.subtle.digest('SHA-256', buffer);
    return Array.from(new Uint8Array(hashBuffer))
        .map(b => b.toString(16).padStart(2, '0'))
        .join('');
}
```

#### Composant Upload Zone
```tsx
// frontend/ts/components/verification/UploadZone.tsx
import React, { useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, FileText } from 'lucide-react';
import { Card } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';

interface UploadZoneProps {
    onUpload: (file: File) => void;
    loading?: boolean;
}

export default function UploadZone({ onUpload, loading }: UploadZoneProps) {
    const onDrop = useCallback((acceptedFiles: File[]) => {
        if (acceptedFiles.length > 0) {
            onUpload(acceptedFiles[0]);
        }
    }, [onUpload]);
    
    const { getRootProps, getInputProps, isDragActive } = useDropzone({
        onDrop,
        accept: {
            'application/pdf': ['.pdf'],
            'image/jpeg': ['.jpg', '.jpeg'],
            'image/png': ['.png'],
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx']
        },
        maxFiles: 1,
        maxSize: 10 * 1024 * 1024 // 10MB
    });
    
    return (
        <Card className="p-8">
            <div
                {...getRootProps()}
                className={`
                    border-2 border-dashed rounded-lg p-12
                    text-center cursor-pointer transition-colors
                    ${isDragActive ? 'border-primary bg-primary/5' : 'border-gray-300'}
                    ${loading ? 'opacity-50 pointer-events-none' : ''}
                `}
            >
                <input {...getInputProps()} />
                
                {loading ? (
                    <>
                        <FileText className="w-16 h-16 mx-auto mb-4 text-primary animate-pulse" />
                        <p className="text-lg font-medium mb-2">Calcul du hash en cours...</p>
                        <Progress value={undefined} className="w-64 mx-auto" />
                    </>
                ) : (
                    <>
                        <Upload className="w-16 h-16 mx-auto mb-4 text-gray-400" />
                        <p className="text-lg font-medium mb-2">
                            {isDragActive
                                ? 'Déposez votre document ici'
                                : 'Glissez votre document ici ou cliquez pour parcourir'}
                        </p>
                        <p className="text-sm text-gray-500">
                            Formats acceptés : PDF, JPG, PNG, DOCX (max 10MB)
                        </p>
                    </>
                )}
            </div>
        </Card>
    );
}
```

## 📝 Conventions de Code

### Backend Django
- **Naming**: `snake_case` pour variables/fonctions
- **Docstrings**: Google style pour toutes les fonctions publiques
- **Type hints**: Utiliser systématiquement
- **Validation**: Pydantic schemas pour API
- **Logs**: Utiliser le logger configuré
```python
import logging
logger = logging.getLogger(__name__)

@api.post("/verify/upload")
def verify_upload(request, file: UploadedFile = File(...)):
    """
    Vérifie l'authenticité d'un document uploadé.
    
    Args:
        request: Django request object
        file: Document à vérifier
        
    Returns:
        VerificationResultSchema: Résultat de la vérification
        
    Raises:
        HttpError: Si fichier invalide ou rate limit atteint
    """
    logger.info(f"Verification request from {request.META['REMOTE_ADDR']}")
    # ...
```

### Frontend React
- **Naming**: `camelCase` pour variables, `PascalCase` pour composants
- **TypeScript**: Typage strict activé
- **Props**: Interfaces explicites
- **Hooks**: Ordre standard (useState, useEffect, customs)
- **Composants**: Fonctionnels uniquement
```tsx
interface ResultCardProps {
    result: VerificationResult;
    className?: string;
}

export default function ResultCard({ result, className }: ResultCardProps) {
    // Logic here
}
```

## 🚀 Plan de Développement

### Étape 1: API Backend (2-3 jours)
1. Créer `apps/verifications/api.py` avec Django Ninja
2. Implémenter endpoints de vérification
3. Implémenter endpoints de signalement
4. Ajouter rate limiting
5. Tester avec curl/Postman

### Étape 2: Services & Logique (1-2 jours)
1. Créer `apps/verifications/services.py`
2. Implémenter `VerificationService.verify_document()`
3. Implémenter génération certificat PDF
4. Ajouter logs audit
5. Background tasks pour notifications

### Étape 3: Frontend Base (2 jours)
1. Créer Layout (`Header.tsx`, `Footer.tsx`, `Layout.tsx`)
2. Créer composants UI Shadcn nécessaires
3. Implémenter page Home (`Home.tsx`)
4. Implémenter page FAQ (`FAQ.tsx`)

### Étape 4: Page Vérification (3-4 jours)
1. Créer `Verify.tsx` avec Tabs
2. Implémenter `UploadZone.tsx`
3. Implémenter `QRScanner.tsx` (html5-qrcode)
4. Implémenter `HashInput.tsx`
5. Implémenter `ResultCard.tsx`
6. Intégrer avec API/Inertia

### Étape 5: Composants Avancés (2 jours)
1. `VerificationHistory.tsx` (localStorage)
2. `ReportModal.tsx` pour signalements
3. Animations et transitions
4. Responsive design final

### Étape 6: Intégration & Polish (1-2 jours)
1. Connecter frontend ↔ backend
2. Gestion erreurs globale
3. Messages toast/notifications
4. Optimisation performance
5. Accessibilité (ARIA labels)

## ⚠️ Contraintes Importantes

### Sécurité
- ✅ Rate limiting sur tous les endpoints publics
- ✅ Validation stricte des inputs (Pydantic)
- ✅ Sanitization des données utilisateur
- ✅ CORS configuré correctement
- ✅ CSRF protection active (Django)
- ❌ Jamais de clés privées côté frontend
- ❌ Jamais de secrets dans le code

### Performance
- Hash calculé **côté client** (Web Crypto API)
- Cache Redis pour résultats fréquents
- Pagination sur listes (25 items/page)
- Lazy loading composants lourds
- Optimisation images (WebP, lazy)

### UX/UI
- Design responsive (mobile-first)
- Loading states partout
- Messages d'erreur clairs
- Feedback visuel immédiat
- Accessibilité WCAG 2.1 AA

## 📦 Livrables Attendus

### Backend
```
apps/verifications/
├── api.py              # Endpoints Django Ninja
├── services.py         # Logique métier
├── schemas.py          # Schémas Pydantic
└── tasks.py            # Background tasks
```

### Frontend
```
frontend/ts/
├── pages/
│   ├── Home.tsx
│   ├── Verify.tsx
│   └── FAQ.tsx
├── components/
│   ├── layout/
│   │   ├── Header.tsx
│   │   ├── Footer.tsx
│   │   └── Layout.tsx
│   ├── verification/
│   │   ├── UploadZone.tsx
│   │   ├── QRScanner.tsx
│   │   ├── HashInput.tsx
│   │   ├── ResultCard.tsx
│   │   └── VerificationHistory.tsx
│   └── reports/
│       └── ReportModal.tsx
└── lib/
    └── utils.ts
```

## 🎨 Design System

### Couleurs Tailwind
```typescript
// tailwind.config.js (déjà configuré)
{
  primary: "hsl(var(--primary))",      // Bleu principal
  success: "hsl(var(--success))",      // Vert (authentique)
  destructive: "hsl(var(--destructive))", // Rouge (invalide)
  warning: "hsl(var(--warning))",      // Orange (non trouvé)
}
```

### Composants Shadcn à Utiliser
- `Button` (variants: default, destructive, outline, ghost)
- `Card` pour conteneurs
- `Tabs` pour méthodes vérification
- `Alert` pour messages (success, error, warning)
- `Dialog` pour modals
- `Progress` pour chargement
- `Badge` pour statuts
- `Table` pour historiques

## 🔍 Exemples de Code Complets

### Route Django avec Inertia
```python
# apps/verifications/views.py
from inertia import render
from django.http import HttpRequest

def verify_page(request: HttpRequest):
    """Page de vérification publique"""
    return render(request, 'Verify', {
        'csrfToken': request.META.get('CSRF_COOKIE'),
        'user': request.user.serialize() if request.user.is_authenticated else None
    })

def verify_submit(request: HttpRequest):
    """Traitement soumission vérification"""
    if request.method == 'POST':
        document_hash = request.POST.get('document_hash')
        result = VerificationService.verify_document(document_hash, get_client_ip(request))
        
        return render(request, 'Verify', {
            'result': result,
            'csrfToken': request.META.get('CSRF_COOKIE')
        })
```

### Appel API depuis React
```tsx
// Alternative: appel direct API au lieu d'Inertia
import axios from 'axios';

const handleVerify = async (hash: string) => {
    try {
        const response = await axios.post('/api/v1/verify/hash', {
            document_hash: hash
        });
        
        setResult(response.data);
    } catch (error) {
        if (error.response?.status === 429) {
            toast.error('Trop de requêtes, réessayez dans 1 minute');
        } else {
            toast.error('Erreur lors de la vérification');
        }
    }
};
```

## 🧪 Validation

### Tests Manuels Requis
- [ ] Upload PDF fonctionne
- [ ] Scan QR code détecte
- [ ] Hash manuel valide
- [ ] Résultat authentique s'affiche correctement
- [ ] Résultat invalide s'affiche correctement
- [ ] Signalement fonctionne
- [ ] Rate limiting bloque après 10 req/min
- [ ] Responsive sur mobile
- [ ] Accessible au clavier

### Checklist Qualité
- [ ] Aucun warning TypeScript
- [ ] Aucune erreur console
- [ ] Logs backend cohérents
- [ ] Temps de réponse < 3s
- [ ] Build production réussit
- [ ] Variables d'environnement documentées

## 📞 Support

En cas de blocage :
1. Consulter `docs/letscheck_architecture.md`
2. Vérifier `.env.example` pour variables
3. Lire README.md pour setup
4. Vérifier logs Django : `python manage.py runserver`
5. Vérifier console navigateur

---

**Commence par l'Étape 1 (API Backend) et progresse séquentiellement. Documente ton code et crée des commits atomiques.**

