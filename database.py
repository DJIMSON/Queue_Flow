"""
database.py - Configuration de la Base de Données
==================================================
Ce fichier configure la connexion à SQLite et crée le moteur de BD.
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# ========== URL DE LA BASE DE DONNÉES ==========
# SQLite stocke tout dans un fichier .db
SQLALCHEMY_DATABASE_URL = "sqlite:///./queueflow.db"
# "./" signifie "dans le dossier actuel"

# ========== CRÉATION DU MOTEUR ==========
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
    # check_same_thread=False : permet plusieurs connexions simultanées
    # (nécessaire pour FastAPI qui est asynchrone)
)

# ========== SESSION LOCALE ==========
SessionLocal = sessionmaker(
    autocommit=False,  # Ne pas sauvegarder automatiquement
    autoflush=False,   # Ne pas synchroniser automatiquement
    bind=engine        # Lier au moteur créé ci-dessus
)
# SessionLocal = "fabrique" de sessions de BD
# Chaque session = une conversation avec la base de données

# ========== BASE POUR LES MODÈLES ==========
Base = declarative_base()
# Toutes nos classes de modèles hériteront de cette Base

# ========== FONCTION POUR OBTENIR UNE SESSION ==========
def get_db():
    """
    Cette fonction crée une session de base de données.
    Elle sera utilisée par FastAPI pour chaque requête.

    Fonctionnement :
    1. Crée une nouvelle session
    2. Yield = "prête" la session à FastAPI
    3. Quand la requête est terminée, ferme la session
    """
    db = SessionLocal()
    try:
        yield db  # "Prête" la session
    finally:
        db.close()  # Ferme la session après utilisation
