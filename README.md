# QueueFlow Backend API 🎫

API de gestion des files d'attente pour institutions (hôpitaux, mairies, banques, transports).

## 📋 Description

Cette API permet de :
- ✅ Gérer plusieurs types d'institutions
- ✅ Créer des tickets numérotés
- ✅ Suivre la position dans la file d'attente
- ✅ Calculer le temps d'attente estimé
- ✅ Vérifier le statut d'un ticket en temps réel

## 🏗️ Architecture

```
queueflow-backend/
├── main.py           # Point d'entrée de l'API (routes FastAPI)
├── models.py         # Modèles de base de données (SQLAlchemy)
├── schemas.py        # Schémas de validation (Pydantic)
├── crud.py           # Opérations sur la BD
├── database.py       # Configuration de la BD
├── run.py            # Script de lancement
├── requirements.txt  # Dépendances Python
└── queueflow.db      # Base de données SQLite (créée automatiquement)
```

## 🚀 Installation

### 1. Prérequis
- Python 3.8 ou supérieur
- pip (gestionnaire de paquets Python)

### 2. Installation des dépendances

```bash
# Créer un environnement virtuel (recommandé)
python -m venv venv

# Activer l'environnement virtuel
# Sur Windows :
venv\Scripts\activate
# Sur Mac/Linux :
source venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt
```

## ▶️ Lancement

### Méthode 1 : Avec le script run.py
```bash
python run.py
```

### Méthode 2 : Avec Uvicorn directement
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

L'API sera accessible sur : **http://localhost:8000**

## 📚 Documentation

Une fois l'API lancée, la documentation interactive est disponible :

- **Swagger UI** : http://localhost:8000/docs
- **ReDoc** : http://localhost:8000/redoc

Ces interfaces permettent de tester directement toutes les routes !

## 🛣️ Routes Principales

### Institutions

| Méthode | Route | Description |
|---------|-------|-------------|
| GET | `/institutions` | Liste toutes les institutions |
| GET | `/institutions/type/{type}` | Institutions par type |
| GET | `/institutions/{id}` | Détails d'une institution |
| POST | `/institutions` | Créer une institution |

### Tickets

| Méthode | Route | Description |
|---------|-------|-------------|
| POST | `/tickets` | **Créer un nouveau ticket** |
| GET | `/tickets/{number}/stats` | **Vérifier un ticket** |
| GET | `/tickets/{number}` | Détails d'un ticket |
| PUT | `/tickets/{number}/status` | Changer le statut |

### Files d'attente

| Méthode | Route | Description |
|---------|-------|-------------|
| GET | `/queue/{institution_id}` | Infos de la file |
| GET | `/queue/details/{institution_id}` | Détails complets |

## 💻 Exemples d'Utilisation

### 1. Créer un Ticket

**Requête :**
```bash
POST /tickets
Content-Type: application/json

{
  "institution_id": 1
}
```

**Réponse :**
```json
{
  "ticket_number": "H001",
  "queue_position": 5,
  "people_ahead": 4,
  "estimated_wait_time": 12,
  "institution_name": "Hôpital Principal de Dakar"
}
```

### 2. Vérifier un Ticket

**Requête :**
```bash
GET /tickets/H001/stats
```

**Réponse :**
```json
{
  "ticket_number": "H001",
  "queue_position": 3,
  "people_ahead": 2,
  "estimated_wait_time": 6,
  "institution_name": "Hôpital Principal de Dakar"
}
```

### 3. Lister les Hôpitaux

**Requête :**
```bash
GET /institutions/type/hospital
```

**Réponse :**
```json
[
  {
    "id": 1,
    "name": "Hôpital Principal de Dakar",
    "type": "hospital",
    "location": "Dakar",
    "address": "Avenue Nelson Mandela, Dakar",
    "phone": "+221 33 839 50 50",
    "created_at": "2026-02-01T00:00:00"
  },
  ...
]
```

## 🗄️ Base de Données

L'API utilise **SQLite** pour le stockage :
- Fichier : `queueflow.db`
- Créé automatiquement au premier lancement
- Initialisé avec 12 institutions de test

### Tables

1. **institutions** : Stocke les établissements
2. **tickets** : Stocke tous les tickets créés
3. **queues** : Gère l'état des files d'attente

## 🔧 Configuration CORS

L'API accepte actuellement toutes les origines (`allow_origins=["*"]`).

**En production**, modifiez dans `main.py` :
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://votre-domaine.com"],  # Votre domaine
    ...
)
```

## 🧪 Tests

### Test manuel avec curl

```bash
# Health check
curl http://localhost:8000/health

# Créer un ticket
curl -X POST http://localhost:8000/tickets \
  -H "Content-Type: application/json" \
  -d '{"institution_id": 1}'

# Vérifier un ticket
curl http://localhost:8000/tickets/H001/stats
```

### Test avec le navigateur

Ouvrez simplement : http://localhost:8000/docs

## 📦 Déploiement

### Option 1 : Serveur Linux
```bash
# Utiliser un process manager comme PM2 ou systemd
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Option 2 : Docker (fichier fourni séparément)
```bash
docker build -t queueflow-api .
docker run -p 8000:8000 queueflow-api
```

### Option 3 : Plateformes cloud
- Heroku
- Railway
- Render
- DigitalOcean App Platform

## 🔐 Sécurité (À ajouter en production)

- [ ] Authentification JWT
- [ ] Rate limiting
- [ ] HTTPS obligatoire
- [ ] Variables d'environnement pour secrets
- [ ] Validation stricte des entrées

## 🐛 Dépannage

### Erreur : "Module not found"
```bash
pip install -r requirements.txt
```

### Port 8000 déjà utilisé
Changez le port dans `run.py` :
```python
uvicorn.run("main:app", port=8001, ...)
```

### Base de données corrompue
Supprimez `queueflow.db` et relancez l'API.

## 📞 Support

Pour toute question, consultez :
- Documentation Swagger : http://localhost:8000/docs
- Documentation FastAPI : https://fastapi.tiangolo.com/
- Documentation SQLAlchemy : https://www.sqlalchemy.org/

---

**Développé avec FastAPI 🚀**
