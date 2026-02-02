# 🎫 QueueFlow - Système de Gestion de Files d'Attente

![QueueFlow](https://img.shields.io/badge/Version-1.0.0-blue)
![Python](https://img.shields.io/badge/Python-3.8+-green)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-teal)
![License](https://img.shields.io/badge/License-MIT-yellow)

QueueFlow est une application web moderne de gestion de files d'attente pour les institutions (hôpitaux, banques, administrations). Elle permet aux utilisateurs de réserver des tickets en ligne et aux opérateurs de gérer efficacement les files d'attente.

## ✨ Fonctionnalités

### 👤 Pour les Utilisateurs
- 📱 Réservation de tickets en ligne
- 🏢 Choix d'institutions et de services
- ⏰ Sélection d'horaires disponibles
- 📊 Visualisation de la position dans la file
- 🔔 Notifications en temps réel

### 👨‍💼 Pour les Opérateurs
- 📢 Appel du prochain ticket
- ✅ Gestion des tickets (appelé, terminé, annulé)
- 📈 Statistiques en temps réel
- 👥 Vue de la file d'attente de leur institution

### 🎛️ Pour les Administrateurs
- 🏢 Gestion des institutions
- 🔧 Gestion des services
- 👥 Création de comptes opérateurs
- 📊 Statistiques globales du système
- 🎫 Vue complète de tous les tickets

## 🛠️ Technologies Utilisées

### Backend
- **FastAPI** - Framework web moderne et performant
- **SQLAlchemy** - ORM pour la base de données
- **SQLite** - Base de données légère
- **Pydantic** - Validation des données
- **Passlib** - Hash sécurisé des mots de passe
- **Uvicorn** - Serveur ASGI

### Frontend
- **HTML5** - Structure
- **CSS3** - Styling moderne avec variables CSS
- **JavaScript (Vanilla)** - Logique frontend
- **Fetch API** - Communication avec le backend

## 📋 Prérequis

- Python 3.8 ou supérieur
- pip (gestionnaire de packages Python)
- Un navigateur web moderne

## 🚀 Installation

### 1. Cloner le repository

```bash
git clone https://github.com/votre-username/QueueFlow.git
cd QueueFlow
```

### 2. Créer un environnement virtuel

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 3. Installer les dépendances

```bash
cd QueueFlow-Backend
pip install -r requirements.txt
```

### 4. Lancer le backend

```bash
uvicorn main:app --reload
```

Le backend sera accessible à : `http://127.0.0.1:8000`

### 5. Ouvrir le frontend

Ouvrez simplement le fichier `QueueFlow-API-Fixed.html` dans votre navigateur.

## 📖 Documentation API

La documentation interactive de l'API est disponible à :
- Swagger UI : `http://127.0.0.1:8000/docs`
- ReDoc : `http://127.0.0.1:8000/redoc`

## 🔐 Comptes de Test

### Utilisateur Standard
- Email : `user@test.com`
- Mot de passe : `test123`

### Opérateur
- Email : `operator@ledantec.sn`
- Mot de passe : `operator123`

### Administrateur
- Email : `admin@queueflow.com`
- Mot de passe : `admin123`

## 📁 Structure du Projet

```
QueueFlow/
├── QueueFlow-Backend/
│   ├── main.py                 # Point d'entrée de l'API
│   ├── database.py             # Configuration base de données
│   ├── models.py               # Modèles SQLAlchemy
│   ├── schemas.py              # Schémas Pydantic
│   ├── requirements.txt        # Dépendances Python
│   └── queueflow.db           # Base de données SQLite
├── QueueFlow-API-Fixed.html   # Frontend de l'application
├── .gitignore                  # Fichiers ignorés par Git
└── README.md                   # Ce fichier
```

## 🔄 Workflow Complet

1. **Utilisateur** crée un compte et réserve un ticket
2. **Système** assigne automatiquement une position dans la file
3. **Opérateur** voit la file d'attente de son institution
4. **Opérateur** appelle le prochain ticket
5. **Utilisateur** est notifié que son ticket est appelé
6. **Opérateur** marque le ticket comme terminé
7. **Système** met à jour les statistiques

## 🌐 Endpoints API Principaux

### Authentification
- `POST /api/auth/signup` - Créer un compte
- `POST /api/auth/login` - Se connecter

### Institutions
- `GET /api/institutions` - Lister les institutions
- `POST /api/institutions` - Créer une institution (Admin)

### Services
- `GET /api/services` - Lister les services
- `POST /api/services` - Créer un service (Admin)

### Tickets
- `GET /api/tickets` - Lister les tickets
- `POST /api/tickets` - Créer un ticket
- `PUT /api/tickets/{id}/call` - Appeler un ticket
- `PUT /api/tickets/{id}/complete` - Terminer un ticket

### Admin
- `GET /api/admin/stats` - Statistiques globales

## 🎨 Captures d'Écran

### Interface Utilisateur
![Interface Utilisateur](screenshots/user-interface.png)

### Dashboard Opérateur
![Dashboard Opérateur](screenshots/operator-dashboard.png)

### Panel Administrateur
![Panel Admin](screenshots/admin-panel.png)

## 🚧 Améliorations Futures

- [ ] Notifications en temps réel (WebSockets)
- [ ] Application mobile (React Native)
- [ ] Impression de tickets PDF
- [ ] Statistiques avancées avec graphiques
- [ ] Support multilingue
- [ ] Système de notifications SMS/Email
- [ ] Mode hors ligne (PWA)

## 🤝 Contribution

Les contributions sont les bienvenues ! Voici comment contribuer :

1. Fork le projet
2. Créez une branche (`git checkout -b feature/AmazingFeature`)
3. Commit vos changements (`git commit -m 'Add some AmazingFeature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrez une Pull Request

## 📝 License

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## 👨‍💻 Auteur

**Maick Broco**
- GitHub: [@votre-username](https://github.com/votre-username)
- Email: votre-email@example.com

## 🙏 Remerciements

- FastAPI pour le framework backend
- La communauté Python pour les excellentes bibliothèques
- Tous les contributeurs du projet

---

⭐ N'oubliez pas de mettre une étoile si ce projet vous a aidé !
