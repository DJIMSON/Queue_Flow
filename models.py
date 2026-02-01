"""
models.py - Modèles de Base de Données CORRIGÉS
================================================
Version étendue avec gestion des utilisateurs et rôles
Relations corrigées avec foreign_keys explicites
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

# Import de la base de données
from database import Base


# ========== ÉNUMÉRATION DES RÔLES UTILISATEURS ==========
class UserRole(str, enum.Enum):
    """Rôles des utilisateurs"""
    CITIZEN = "citizen"      # Citoyen
    OPERATOR = "operator"    # Opérateur (employé institution)
    ADMIN = "admin"          # Administrateur


# ========== ÉNUMÉRATION DES TYPES D'INSTITUTIONS ==========
class InstitutionType(str, enum.Enum):
    """Types d'institutions disponibles"""
    HOSPITAL = "hospital"
    MAIRIE = "mairie"
    BANQUE = "banque"
    TRANSPORT = "transport"


# ========== ÉNUMÉRATION DES STATUTS DE TICKETS ==========
class TicketStatus(str, enum.Enum):
    """Statuts possibles pour un ticket"""
    WAITING = "waiting"         # En attente
    CALLED = "called"           # Appelé
    IN_SERVICE = "in_service"   # En service
    COMPLETED = "completed"     # Terminé
    CANCELLED = "cancelled"     # Annulé
    MISSED = "missed"           # Manqué (pas venu)


# ========== TABLE USER ==========
class User(Base):
    """
    Table des utilisateurs du système
    Gère citoyens, opérateurs et administrateurs
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    password = Column(String, nullable=False)
    role = Column(Enum(UserRole), default=UserRole.CITIZEN)

    # Pour les opérateurs : institution où ils travaillent
    institution_id = Column(Integer, ForeignKey("institutions.id"), nullable=True)

    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)

    # Relations
    institution = relationship("Institution", back_populates="operators")

    # CORRECTION : Spécifier foreign_keys pour éviter l'ambiguïté
    tickets = relationship(
        "Ticket",
        back_populates="user",
        foreign_keys="Ticket.user_id"
    )


# ========== TABLE INSTITUTION ==========
class Institution(Base):
    """Table qui stocke les informations des institutions"""
    __tablename__ = "institutions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    type = Column(Enum(InstitutionType), nullable=False)
    location = Column(String, nullable=False)
    address = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relations
    tickets = relationship("Ticket", back_populates="institution")
    operators = relationship("User", back_populates="institution")


# ========== TABLE TICKET ==========
class Ticket(Base):
    """Table qui stocke les tickets créés par les utilisateurs"""
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, index=True)
    ticket_number = Column(String, unique=True, nullable=False)

    # Lien avec l'utilisateur qui a créé le ticket
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    institution_id = Column(Integer, ForeignKey("institutions.id"), nullable=False)
    status = Column(Enum(TicketStatus), default=TicketStatus.WAITING)
    queue_position = Column(Integer, nullable=False)

    # Opérateur qui a traité le ticket
    operator_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    called_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    # Relations
    institution = relationship("Institution", back_populates="tickets")

    # CORRECTION : Spécifier foreign_keys explicitement
    user = relationship(
        "User",
        back_populates="tickets",
        foreign_keys=[user_id]
    )

    # Pas de back_populates pour operator (relation one-way)
    operator = relationship(
        "User",
        foreign_keys=[operator_id]
    )


# ========== TABLE QUEUE (File d'attente) ==========
class Queue(Base):
    """Table pour gérer l'état actuel des files d'attente"""
    __tablename__ = "queues"

    id = Column(Integer, primary_key=True, index=True)
    institution_id = Column(Integer, ForeignKey("institutions.id"), nullable=False, unique=True)
    current_ticket_number = Column(String, nullable=True)
    last_ticket_number = Column(Integer, default=0)
    total_tickets_today = Column(Integer, default=0)
    average_service_time = Column(Integer, default=3)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
