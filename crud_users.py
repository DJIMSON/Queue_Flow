"""
crud_users.py - Opérations CRUD pour Users et Auth
==================================================
Fonctions pour gérer les utilisateurs et l'authentification
"""

from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime
from typing import List, Optional

import models
import schemas


# ========================================
# GESTION DES UTILISATEURS
# ========================================

def get_user_by_email(db: Session, email: str) -> Optional[models.User]:
    """
    Récupère un utilisateur par son email
    """
    return db.query(models.User).filter(models.User.email == email).first()


def get_user_by_id(db: Session, user_id: int) -> Optional[models.User]:
    """
    Récupère un utilisateur par son ID
    """
    return db.query(models.User).filter(models.User.id == user_id).first()


def create_user(db: Session, user: schemas.UserCreate) -> models.User:
    """
    Crée un nouvel utilisateur

    NOTE: En production, TOUJOURS hasher le mot de passe!
    Exemple avec bcrypt:
        from passlib.context import CryptContext
        pwd_context = CryptContext(schemes=["bcrypt"])
        hashed_password = pwd_context.hash(user.password)
    """
    # Vérifier si l'email existe déjà
    existing_user = get_user_by_email(db, user.email)
    if existing_user:
        raise ValueError("Un utilisateur avec cet email existe déjà")

    # Pour la démo, on stocke le mot de passe en clair
    # EN PRODUCTION : HASHER LE MOT DE PASSE !
    db_user = models.User(
        name=user.name,
        email=user.email,
        password=user.password,  # À hasher en production
        role=user.role,
        institution_id=user.institution_id
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user


def authenticate_user(db: Session, email: str, password: str) -> Optional[models.User]:
    """
    Authentifie un utilisateur

    NOTE: En production, comparer avec le hash
    Exemple:
        if not pwd_context.verify(password, user.password):
            return None
    """
    user = get_user_by_email(db, email)

    if not user:
        return None

    # Pour la démo, comparaison simple
    # EN PRODUCTION : VÉRIFIER LE HASH !
    if user.password != password:
        return None

    # Mettre à jour last_login
    user.last_login = datetime.utcnow()
    db.commit()

    return user


def get_operators_by_institution(db: Session, institution_id: int) -> List[models.User]:
    """
    Récupère tous les opérateurs d'une institution
    """
    return db.query(models.User).filter(
        models.User.role == models.UserRole.OPERATOR,
        models.User.institution_id == institution_id,
        models.User.is_active == True
    ).all()


def get_all_operators(db: Session) -> List[models.User]:
    """
    Récupère tous les opérateurs (pour admin)
    """
    return db.query(models.User).filter(
        models.User.role == models.UserRole.OPERATOR,
        models.User.is_active == True
    ).all()


# ========================================
# OPÉRATIONS SPÉCIFIQUES AUX OPÉRATEURS
# ========================================

def call_next_ticket(db: Session, institution_id: int, operator_id: int) -> Optional[models.Ticket]:
    """
    Appelle le prochain ticket en attente pour une institution
    """
    # Trouver le premier ticket en attente
    next_ticket = db.query(models.Ticket).filter(
        models.Ticket.institution_id == institution_id,
        models.Ticket.status == models.TicketStatus.WAITING
    ).order_by(models.Ticket.queue_position).first()

    if not next_ticket:
        return None

    # Changer le statut à CALLED
    next_ticket.status = models.TicketStatus.CALLED
    next_ticket.called_at = datetime.utcnow()
    next_ticket.operator_id = operator_id

    # Mettre à jour la queue
    queue = db.query(models.Queue).filter(
        models.Queue.institution_id == institution_id
    ).first()

    if queue:
        queue.current_ticket_number = next_ticket.ticket_number
        queue.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(next_ticket)

    return next_ticket


def complete_ticket(db: Session, ticket_number: str, operator_id: int) -> Optional[models.Ticket]:
    """
    Marque un ticket comme complété
    """
    ticket = db.query(models.Ticket).filter(
        models.Ticket.ticket_number == ticket_number
    ).first()

    if not ticket:
        return None

    ticket.status = models.TicketStatus.COMPLETED
    ticket.completed_at = datetime.utcnow()
    ticket.operator_id = operator_id

    db.commit()
    db.refresh(ticket)

    return ticket


def mark_ticket_missed(db: Session, ticket_number: str) -> Optional[models.Ticket]:
    """
    Marque un ticket comme manqué
    """
    ticket = db.query(models.Ticket).filter(
        models.Ticket.ticket_number == ticket_number
    ).first()

    if not ticket:
        return None

    ticket.status = models.TicketStatus.MISSED

    db.commit()
    db.refresh(ticket)

    return ticket


def get_operator_stats(db: Session, operator_id: int, date: datetime = None) -> dict:
    """
    Récupère les statistiques d'un opérateur
    """
    if date is None:
        date = datetime.utcnow().date()

    # Tickets servis aujourd'hui
    tickets_served = db.query(models.Ticket).filter(
        models.Ticket.operator_id == operator_id,
        models.Ticket.status == models.TicketStatus.COMPLETED,
        func.date(models.Ticket.completed_at) == date
    ).count()

    # Ticket actuel
    current_ticket = db.query(models.Ticket).filter(
        models.Ticket.operator_id == operator_id,
        models.Ticket.status.in_([models.TicketStatus.CALLED, models.TicketStatus.IN_SERVICE])
    ).first()

    return {
        "tickets_served_today": tickets_served,
        "current_ticket": current_ticket.ticket_number if current_ticket else None
    }


# ========================================
# OPÉRATIONS ADMIN
# ========================================

def get_admin_stats(db: Session) -> dict:
    """
    Récupère les statistiques globales pour l'admin
    """
    today = datetime.utcnow().date()

    total_institutions = db.query(models.Institution).count()
    total_users = db.query(models.User).count()
    total_operators = db.query(models.User).filter(
        models.User.role == models.UserRole.OPERATOR
    ).count()

    total_tickets_today = db.query(models.Ticket).filter(
        func.date(models.Ticket.created_at) == today
    ).count()

    tickets_waiting = db.query(models.Ticket).filter(
        models.Ticket.status == models.TicketStatus.WAITING
    ).count()

    tickets_completed = db.query(models.Ticket).filter(
        models.Ticket.status == models.TicketStatus.COMPLETED,
        func.date(models.Ticket.completed_at) == today
    ).count()

    tickets_missed = db.query(models.Ticket).filter(
        models.Ticket.status == models.TicketStatus.MISSED,
        func.date(models.Ticket.created_at) == today
    ).count()

    return {
        "total_institutions": total_institutions,
        "total_users": total_users,
        "total_operators": total_operators,
        "total_tickets_today": total_tickets_today,
        "tickets_waiting": tickets_waiting,
        "tickets_completed": tickets_completed,
        "tickets_missed": tickets_missed,
        "average_wait_time": 3  # À calculer dynamiquement
    }


def get_user_ticket_history(db: Session, user_id: int, limit: int = 10) -> List[models.Ticket]:
    """
    Récupère l'historique des tickets d'un utilisateur
    """
    return db.query(models.Ticket).filter(
        models.Ticket.user_id == user_id
    ).order_by(models.Ticket.created_at.desc()).limit(limit).all()
