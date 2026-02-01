"""
schemas.py - Schémas Pydantic ÉTENDUS
=====================================
Version étendue avec authentification et gestion utilisateurs
"""

from pydantic import BaseModel, Field, EmailStr
from datetime import datetime
from typing import Optional, List
from models import InstitutionType, TicketStatus, UserRole


# ========== SCHÉMAS POUR USER ==========

class UserBase(BaseModel):
    """Schéma de base pour User"""
    name: str = Field(..., min_length=2, description="Nom complet")
    email: EmailStr = Field(..., description="Email unique")


class UserCreate(UserBase):
    """Schéma pour créer un utilisateur (signup)"""
    password: str = Field(..., min_length=6, description="Mot de passe")
    role: Optional[UserRole] = UserRole.CITIZEN
    institution_id: Optional[int] = None


class UserLogin(BaseModel):
    """Schéma pour se connecter"""
    email: EmailStr
    password: str


class UserResponse(UserBase):
    """Schéma pour renvoyer un utilisateur (sans mot de passe!)"""
    id: int
    role: UserRole
    institution_id: Optional[int]
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime]

    class Config:
        from_attributes = True


class UserWithToken(UserResponse):
    """Réponse après login avec token (pour future JWT)"""
    token: Optional[str] = "session_active"


# ========== SCHÉMAS POUR INSTITUTION (inchangés mais complétés) ==========

class InstitutionBase(BaseModel):
    """Schéma de base pour Institution"""
    name: str = Field(..., description="Nom de l'institution")
    type: InstitutionType
    location: str
    address: Optional[str] = None
    phone: Optional[str] = None


class InstitutionCreate(InstitutionBase):
    """Schéma pour créer une institution"""
    pass


class InstitutionUpdate(BaseModel):
    """Schéma pour modifier une institution"""
    name: Optional[str] = None
    location: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None


class InstitutionResponse(InstitutionBase):
    """Schéma pour renvoyer une institution"""
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# ========== SCHÉMAS POUR TICKET (étendus) ==========

class TicketBase(BaseModel):
    """Schéma de base pour Ticket"""
    institution_id: int = Field(..., description="ID de l'institution")


class TicketCreate(TicketBase):
    """Schéma pour créer un ticket"""
    user_id: Optional[int] = None  # Pour tickets avec utilisateur connecté


class TicketResponse(BaseModel):
    """Schéma pour renvoyer un ticket complet"""
    id: int
    ticket_number: str
    user_id: Optional[int]
    institution_id: int
    status: TicketStatus
    queue_position: int
    operator_id: Optional[int]
    created_at: datetime
    called_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    # Informations de l'institution
    institution: InstitutionResponse

    class Config:
        from_attributes = True


class TicketStatusUpdate(BaseModel):
    """Schéma pour changer le statut d'un ticket"""
    status: TicketStatus
    operator_id: Optional[int] = None


class TicketStats(BaseModel):
    """Statistiques d'un ticket créé"""
    ticket_number: str
    queue_position: int
    people_ahead: int
    estimated_wait_time: int
    institution_name: str


# ========== SCHÉMAS POUR QUEUE ==========

class QueueInfo(BaseModel):
    """Schéma pour les informations de file d'attente"""
    institution_id: int
    current_ticket_number: Optional[str] = None
    people_waiting: int = Field(..., description="Nombre de personnes en attente")
    estimated_wait_time: int = Field(..., description="Temps d'attente estimé (minutes)")
    average_service_time: int


class QueueResponse(BaseModel):
    """Schéma pour renvoyer l'état complet d'une queue"""
    id: int
    institution_id: int
    current_ticket_number: Optional[str]
    last_ticket_number: int
    total_tickets_today: int
    average_service_time: int
    updated_at: datetime

    class Config:
        from_attributes = True


# ========== SCHÉMAS POUR OPÉRATEURS ==========

class OperatorStats(BaseModel):
    """Statistiques d'un opérateur"""
    user_id: int
    name: str
    tickets_served_today: int
    average_service_time: int
    current_ticket: Optional[str] = None


class NextTicketResponse(BaseModel):
    """Réponse quand un opérateur appelle le prochain ticket"""
    ticket: Optional[TicketResponse]
    message: str


# ========== SCHÉMAS POUR ADMIN ==========

class AdminStats(BaseModel):
    """Statistiques globales pour l'administrateur"""
    total_institutions: int
    total_users: int
    total_operators: int
    total_tickets_today: int
    tickets_waiting: int
    tickets_completed: int
    tickets_missed: int
    average_wait_time: int


class InstitutionList(BaseModel):
    """Liste d'institutions par type"""
    institutions: List[InstitutionResponse]
    total: int


# ========== MESSAGES DE RÉPONSE ==========

class Message(BaseModel):
    """Message générique pour les réponses"""
    message: str
    success: bool = True
