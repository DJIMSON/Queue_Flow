"""
crud.py - Opérations CRUD (Create, Read, Update, Delete)
========================================================
Ce fichier contient toutes les fonctions pour interagir avec la BD.
CRUD = Create (Créer), Read (Lire), Update (Modifier), Delete (Supprimer)
"""

from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from typing import List, Optional

import models
import schemas


# ========================================
# OPÉRATIONS SUR LES INSTITUTIONS
# ========================================

def get_institutions(db: Session, skip: int = 0, limit: int = 100) -> List[models.Institution]:
    """
    Récupère toutes les institutions

    Args:
        db: Session de base de données
        skip: Nombre d'éléments à sauter (pagination)
        limit: Nombre maximum d'éléments à retourner

    Returns:
        Liste d'institutions
    """
    return db.query(models.Institution).offset(skip).limit(limit).all()


def get_institutions_by_type(db: Session, institution_type: models.InstitutionType) -> List[models.Institution]:
    """
    Récupère les institutions par type (hospital, mairie, etc.)

    Args:
        db: Session de base de données
        institution_type: Type d'institution (enum)

    Returns:
        Liste d'institutions du type demandé
    """
    return db.query(models.Institution).filter(
        models.Institution.type == institution_type
    ).all()


def get_institution_by_id(db: Session, institution_id: int) -> Optional[models.Institution]:
    """
    Récupère une institution par son ID

    Args:
        db: Session de base de données
        institution_id: ID de l'institution

    Returns:
        L'institution ou None si non trouvée
    """
    return db.query(models.Institution).filter(
        models.Institution.id == institution_id
    ).first()


def create_institution(db: Session, institution: schemas.InstitutionCreate) -> models.Institution:
    """
    Crée une nouvelle institution

    Args:
        db: Session de base de données
        institution: Données de l'institution (schema Pydantic)

    Returns:
        L'institution créée
    """
    # Convertir le schéma Pydantic en modèle SQLAlchemy
    db_institution = models.Institution(**institution.model_dump())

    # Ajouter à la session
    db.add(db_institution)

    # Sauvegarder dans la BD
    db.commit()

    # Rafraîchir pour obtenir l'ID généré
    db.refresh(db_institution)

    # Créer une queue pour cette institution
    create_queue_for_institution(db, db_institution.id)

    return db_institution


# ========================================
# OPÉRATIONS SUR LES QUEUES
# ========================================

def create_queue_for_institution(db: Session, institution_id: int) -> models.Queue:
    """
    Crée une file d'attente pour une institution

    Args:
        db: Session de base de données
        institution_id: ID de l'institution

    Returns:
        La queue créée
    """
    db_queue = models.Queue(
        institution_id=institution_id,
        last_ticket_number=0,
        total_tickets_today=0,
        average_service_time=3
    )
    db.add(db_queue)
    db.commit()
    db.refresh(db_queue)
    return db_queue


def get_queue_by_institution(db: Session, institution_id: int) -> Optional[models.Queue]:
    """
    Récupère la queue d'une institution

    Args:
        db: Session de base de données
        institution_id: ID de l'institution

    Returns:
        La queue ou None
    """
    return db.query(models.Queue).filter(
        models.Queue.institution_id == institution_id
    ).first()


def get_queue_info(db: Session, institution_id: int) -> Optional[schemas.QueueInfo]:
    """
    Récupère les informations détaillées de la file d'attente

    Args:
        db: Session de base de données
        institution_id: ID de l'institution

    Returns:
        Informations de la queue (QueueInfo schema)
    """
    queue = get_queue_by_institution(db, institution_id)
    if not queue:
        return None

    # Compter le nombre de personnes en attente
    people_waiting = db.query(models.Ticket).filter(
        models.Ticket.institution_id == institution_id,
        models.Ticket.status == models.TicketStatus.WAITING
    ).count()

    # Calculer le temps d'attente estimé
    estimated_wait_time = people_waiting * queue.average_service_time

    return schemas.QueueInfo(
        institution_id=institution_id,
        current_ticket_number=queue.current_ticket_number,
        people_waiting=people_waiting,
        estimated_wait_time=estimated_wait_time,
        average_service_time=queue.average_service_time
    )


# ========================================
# OPÉRATIONS SUR LES TICKETS
# ========================================

def generate_ticket_number(db: Session, institution_id: int) -> str:
    """
    Génère un numéro de ticket unique
    Format: A001, A002, B001, etc.

    Args:
        db: Session de base de données
        institution_id: ID de l'institution

    Returns:
        Numéro de ticket (string)
    """
    queue = get_queue_by_institution(db, institution_id)

    if not queue:
        # Si pas de queue, en créer une
        queue = create_queue_for_institution(db, institution_id)

    # Incrémenter le dernier numéro
    queue.last_ticket_number += 1
    queue.total_tickets_today += 1

    # Générer le numéro
    # Lettre basée sur le type d'institution
    institution = get_institution_by_id(db, institution_id)
    letter_map = {
        models.InstitutionType.HOSPITAL: "H",
        models.InstitutionType.MAIRIE: "M",
        models.InstitutionType.BANQUE: "B",
        models.InstitutionType.TRANSPORT: "T"
    }
    letter = letter_map.get(institution.type, "A")

    # Format: H001, H002, etc.
    ticket_number = f"{letter}{queue.last_ticket_number:03d}"

    db.commit()
    db.refresh(queue)

    return ticket_number


def create_ticket(db: Session, ticket: schemas.TicketCreate) -> models.Ticket:
    """
    Crée un nouveau ticket

    Args:
        db: Session de base de données
        ticket: Données du ticket (TicketCreate schema)

    Returns:
        Le ticket créé
    """
    # Vérifier que l'institution existe
    institution = get_institution_by_id(db, ticket.institution_id)
    if not institution:
        raise ValueError(f"Institution {ticket.institution_id} n'existe pas")

    # Générer le numéro de ticket
    ticket_number = generate_ticket_number(db, ticket.institution_id)

    # Calculer la position dans la queue
    queue_position = db.query(models.Ticket).filter(
        models.Ticket.institution_id == ticket.institution_id,
        models.Ticket.status == models.TicketStatus.WAITING
    ).count() + 1

    # Créer le ticket
    db_ticket = models.Ticket(
        ticket_number=ticket_number,
        institution_id=ticket.institution_id,
        status=models.TicketStatus.WAITING,
        queue_position=queue_position
    )

    db.add(db_ticket)
    db.commit()
    db.refresh(db_ticket)

    return db_ticket


def get_ticket_by_number(db: Session, ticket_number: str) -> Optional[models.Ticket]:
    """
    Récupère un ticket par son numéro

    Args:
        db: Session de base de données
        ticket_number: Numéro du ticket

    Returns:
        Le ticket ou None
    """
    return db.query(models.Ticket).filter(
        models.Ticket.ticket_number == ticket_number
    ).first()


def get_ticket_stats(db: Session, ticket_number: str) -> Optional[schemas.TicketStats]:
    """
    Récupère les statistiques d'un ticket

    Args:
        db: Session de base de données
        ticket_number: Numéro du ticket

    Returns:
        Statistiques du ticket (TicketStats schema)
    """
    ticket = get_ticket_by_number(db, ticket_number)
    if not ticket:
        return None

    # Compter les personnes devant
    people_ahead = db.query(models.Ticket).filter(
        models.Ticket.institution_id == ticket.institution_id,
        models.Ticket.status == models.TicketStatus.WAITING,
        models.Ticket.queue_position < ticket.queue_position
    ).count()

    # Obtenir la queue pour le temps d'attente
    queue = get_queue_by_institution(db, ticket.institution_id)
    estimated_wait_time = people_ahead * queue.average_service_time if queue else 0

    return schemas.TicketStats(
        ticket_number=ticket.ticket_number,
        queue_position=ticket.queue_position,
        people_ahead=people_ahead,
        estimated_wait_time=estimated_wait_time,
        institution_name=ticket.institution.name
    )


def update_ticket_status(db: Session, ticket_number: str, status: models.TicketStatus) -> Optional[models.Ticket]:
    """
    Met à jour le statut d'un ticket

    Args:
        db: Session de base de données
        ticket_number: Numéro du ticket
        status: Nouveau statut

    Returns:
        Le ticket mis à jour ou None
    """
    ticket = get_ticket_by_number(db, ticket_number)
    if not ticket:
        return None

    ticket.status = status

    # Mettre à jour les timestamps selon le statut
    if status == models.TicketStatus.CALLED:
        ticket.called_at = datetime.utcnow()
    elif status == models.TicketStatus.COMPLETED:
        ticket.completed_at = datetime.utcnow()

    db.commit()
    db.refresh(ticket)

    return ticket


def get_waiting_tickets_by_institution(db: Session, institution_id: int) -> List[models.Ticket]:
    """
    Récupère tous les tickets en attente pour une institution

    Args:
        db: Session de base de données
        institution_id: ID de l'institution

    Returns:
        Liste des tickets en attente, triés par position
    """
    return db.query(models.Ticket).filter(
        models.Ticket.institution_id == institution_id,
        models.Ticket.status == models.TicketStatus.WAITING
    ).order_by(models.Ticket.queue_position).all()
