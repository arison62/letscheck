Let's Check (L'sC) est un système de vérification d'authenticité des documents numériques et physiques destiné aux institutions publiques et privées


## 📋 Table des matières

- [Technologies utilisées](#technologies-utilisées)
- [Architecture du projet](#architecture-du-projet)
- [Prérequis](#prérequis)
- [Installation](#installation)
- [Configuration](#configuration)
- [Développement](#développement)
- [Structure du projet](#structure-du-projet)
- [Ressources et documentation](#ressources-et-documentation)
- [Contribution](#contribution)


## 🛠 Technologies utilisées

### Backend
- **[Django](https://www.djangoproject.com/)** (≥ 5.0) - Framework web Python mature avec sécurité intégrée
- **[PostgreSQL](https://www.postgresql.org/)** (≥ 15) - Base de données relationnelle robuste
- **[Inertia-Django](https://inertiajs.github.io/inertia-django/)** - Bridge pour intégrer React sans API REST

### Frontend
- **[React.js](https://react.dev/)** (≥ 18) - Bibliothèque JavaScript pour interfaces réactives
- **[Inertia.js](https://inertiajs.com/)** - Créer des SPA avec backends monolithiques
- **[Vite](https://vitejs.dev/)** - Build tool moderne et rapide
- **[Tailwind CSS](https://tailwindcss.com/)** - Framework CSS utility-first
- **[Shadcn UI](https://ui.shadcn.com/)** - Collection de composants React réutilisables

### Pourquoi ce stack ?

- ✅ **Django** : Sécurité robuste (authentification, protection XSS/CSRF, injection SQL)
- ✅ **Inertia-Django** : Intégration React sans complexité API REST
- ✅ **React.js** : Performance et réactivité côté frontend
- ✅ **Shadcn UI** : Composants prêts à l'emploi, personnalisables
- ✅ **Tailwind CSS** : Styling rapide et responsive
- ✅ **PostgreSQL** : Gestion de données complexes avec performance

## 📁 Architecture du projet

```
letscheck_web/
├── letscheck_web/             # Configuration Django principale
│   ├── settings.py        # Paramètres du projet
│   ├── urls.py            # Routes principales
│   └── wsgi.py            # Point d'entrée WSGI
├── frontend/              # Ressources frontend (React + Vite)
│   ├──  main.css          # Styles generer par tailwindcss
│   │                      
│   │                     
│   └── ts/                # Fichiers JavaScript/React
│       ├── components/    # Composants React réutilisables
│       ├── lib/           # Utilitaires (cn helper, etc.)
│       ├── pages/         # Composants pages Inertia
│       └── main.tsx       # Point d'entrée React/Inertia
├── templates/             # Templates Django de base
│   └── inertia_base.html  # Template racine pour Inertia
│   └── base.html          # Template racine pour Django
├── docs/                  # Documentation du projet
├── static/                # Fichiers statiques (CSS, JS compilés)
├── media/                 # Fichiers uploadés par les utilisateurs
├── components.json        # Configuration Shadcn UI
├── package.json           # Dépendances Node.js
├── requirements.txt       # Dépendances Python
├── vite.config.ts         # Configuration Vite
├── .env.example           # Exemple de variables d'environnement
├── .env                   # Variables d'environnement (non versionné)
├── manage.py              # Utilitaire Django
└── README.md              # Ce fichier
```

## 💻 Prérequis

Avant de commencer, assurez-vous d'avoir installé :

- **Python** ≥ 3.10 ([Télécharger](https://www.python.org/downloads/))
- **PostgreSQL** ≥ 14 ([Télécharger](https://www.postgresql.org/download/))
- **Node.js** ≥ 20.x ([Télécharger](https://nodejs.org/))
- **npm** ou **yarn** (inclus avec Node.js)
- **Git** ([Télécharger](https://git-scm.com/downloads))

Vérifiez vos versions :
```bash
python --version
psql --version
node --version
npm --version
```

## 🚀 Installation

### 1. Cloner le projet

```bash
git clone https://github.com/arison62/letscheck_web.git
cd letscheck_web
```

### 2. Configurer l'environnement Python

Créer et activer l'environnement virtuel :

**Linux/macOS :**
```bash
python -m venv .venv
source .venv/bin/activate
```

**Windows :**
```bash
python -m venv .venv
.venv\Scripts\activate
```

### 3. Installer les dépendances Python

```bash
pip install -r requirements.txt
```

### 4. Installer les dépendances Node.js

```bash
npm install
```

## ⚙️ Configuration

### 1. Variables d'environnement

Copier le fichier exemple et le configurer :

```bash
cp .env.example .env
```

Éditer le fichier `.env` avec vos paramètres :

```env
# Django
SECRET_KEY=votre-clé-secrète-django
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Base de données PostgreSQL (format URL)
DATABASE_URL=postgresql://utilisateur:mot_de_passe@localhost:5432/letscheck_web_db

# Autres configurations
DJANGO_SETTINGS_MODULE=letscheck_web.settings
```

### 2. Créer la base de données PostgreSQL

Connectez-vous à PostgreSQL et créez la base de données :

```bash
psql -U postgres
```

Dans le shell PostgreSQL :
```sql
CREATE DATABASE immob_db;
CREATE USER votre_utilisateur_postgres WITH PASSWORD 'votre_mot_de_passe';
ALTER ROLE votre_utilisateur_postgres SET client_encoding TO 'utf8';
ALTER ROLE votre_utilisateur_postgres SET default_transaction_isolation TO 'read committed';
ALTER ROLE votre_utilisateur_postgres SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE immob_db TO votre_utilisateur_postgres;
\q
```

### 3. Appliquer les migrations

```bash
python manage.py migrate
```

### 4. Créer un superutilisateur (optionnel)

```bash
python manage.py createsuperuser
```

## 🔧 Développement

### Lancer le projet en mode développement

Vous devez lancer **deux serveurs simultanément** dans des terminaux séparés :

**Terminal 1 - Serveur Django (backend) :**
```bash
source .venv/bin/activate  # Activer l'environnement virtuel
python manage.py runserver
```
Le serveur Django sera accessible sur `http://localhost:8000`

**Terminal 2 - Serveur Vite (frontend) :**
```bash
npm run dev
```
Le serveur Vite compilera les assets frontend en temps réel.

**Terminal 3 - Build des fichiers css pour Django :**
```bash
npm run css:dev

> **Note :** En développement, Django sert l'application et Vite compile les assets React/Tailwind en hot-reload.

### Commandes utiles

#### Django

```bash
# Créer une nouvelle app Django
python manage.py startapp nom_app

# Créer des migrations
python manage.py makemigrations

# Appliquer les migrations
python manage.py migrate

# Lancer le shell Django
python manage.py shell

# Collecter les fichiers statiques (production)
python manage.py collectstatic
```

#### Frontend

```bash
# Installer un composant Shadcn UI
npx shadcn@latest add button
npx shadcn@latest add card
npx shadcn@latest add dialog

# Build de production
npm run build

# Linter le code JavaScript
npm run lint
```

#### Inertia.js

Dans vos vues Django, retournez une réponse Inertia :

```python
from inertia import render

def render_inertia(request):
    return render(request, 'Dashboard', {
        'user': request.user.serialize(),
        'stats': get_statistics()
    })
# Le composant React correspondant dans `frontend/ts/pages/Dashboard.tsx` :
```
```python

from django.shortcuts import render

def render_django_template(request):
    return render(request, 'base.html', {})
```

Le composant React correspondant dans `frontend/ts/pages/Dashboard.tsx` :

```tsx
import React from 'react';
import { Head } from '@inertiajs/react';

export default function Dashboard({ user, stats }) {
    return (
        <>
            <Head title="Tableau de bord" />
            <div className="container mx-auto p-4">
                <h1 className="text-3xl font-bold">Bienvenue {user.name}</h1>
                {/* Votre contenu */}
            </div>
        </>
    );
}
```

## 📚 Structure du projet

### Organisation des composants React

```
frontend/
├── main.css                 # Styles generer par tailwindcss
└── js/
    ├── main.tsx               # Point d'entrée Inertia/React
    ├── pages/                 # Pages Inertia (routes)
    │   ├── Dashboard.tsx
    │   ├── Properties/
    │   │   ├── Index.tsx
    │   │   ├── Show.tsx
    │   │   └── Create.tsx
    │   └── Auth/
    │       ├── Login.tsx
    │       └── Register.tsx
    ├── components/            # Composants réutilisables
    │   ├── ui/               # Composants Shadcn UI
    │   │   ├── button.tsx
    │   │   ├── card.tsx
    │   │   └── ...
    │   ├── layout/
    │   │   ├── Header.tsx
    │   │   └── Sidebar.tsx
    │   └── PropertyCard.tsx
    └── lib/
        └── utils.ts          # Utilitaires (cn helper, etc.)
```

### Modèles Django (exemple)

```python
from django.db import models
from django.contrib.auth.models import User

class Stage(models.Model):
    titre = models.CharField(max_length=200)
    description = models.TextField()
    entreprise = models.CharField(max_length=100)
    date_debut = models.DateField()
    date_fin = models.DateField()
    lieu = models.CharField(max_length=100)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.titre
```

## 📖 Ressources et documentation

### Documentation officielle

- **Django** : https://docs.djangoproject.com/
- **Django Tutorial (MDN)** : https://developer.mozilla.org/en-US/docs/Learn/Server-side/Django
- **PostgreSQL** : https://www.postgresql.org/docs/
- **Inertia.js** : https://inertiajs.com/
- **Inertia-Django** : https://inertiajs.github.io/inertia-django/
- **React** : https://react.dev/learn
- **Vite** : https://vitejs.dev/guide/
- **Tailwind CSS** : https://tailwindcss.com/docs
- **Shadcn UI** : https://ui.shadcn.com/docs

### Tutoriels recommandés

- [Django Girls Tutorial](https://tutorial.djangogirls.org/)
- [React Beta Docs](https://react.dev/learn)
- [Tailwind CSS Tutorial](https://tailwindcss.com/docs/installation)
- [Inertia.js Documentation](https://inertiajs.com/the-protocol)

### Dépannage courant

#### Erreur de connexion PostgreSQL
- Vérifiez que PostgreSQL est démarré : `sudo service postgresql status`
- Vérifiez les credentials dans `.env`

#### Erreur Inertia "Page component not found"
- Vérifiez que le composant existe dans `frontend/ts/pages/`
- Le nom doit correspondre exactement (sensible à la casse)

#### Assets non chargés en développement
- Assurez-vous que `npm run dev` est en cours d'exécution
- Vérifiez la configuration Vite dans `vite.config.ts`

#### Composant Shadcn UI non trouvé
- Réinstallez le composant : `npx shadcn@latest add nom-composant`
- Vérifiez le chemin d'import dans `components.json`

## 🤝 Contribution

Les contributions sont les bienvenues ! Pour contribuer :

1. Fork le projet
2. Créez une branche pour votre fonctionnalité (`git checkout -b feature/AmazingFeature`)
3. Committez vos changements (`git commit -m 'Add some AmazingFeature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrez une Pull Request

### Standards de code

- **Python** : Suivre PEP 8
- **TypeScript** : Utiliser ESLint (config fournie)
- **Commits** : Messages clairs et descriptifs en français ou anglais

## 👥 Équipe

Développé avec ❤️ par l'équipe de développement.

---

**Questions ?** Ouvrez une issue sur GitHub ou contactez l'équipe de développement.

🚀 Bon développement !