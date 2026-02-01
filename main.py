"""
main.py - API FastAPI ÉTENDUE
===============================
Version complète avec authentification et gestion multi-rôles
"""

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List

import models
import schemas
import crud
import crud_users
from database import engine, get_db

# ========================================
# CRÉATION DE L'APPLICATION FASTAPI
# ========================================

app = FastAPI(
    title="QueueFlow API Extended",
    description="API complète avec authentification et gestion des rôles",
    version="2.0.0"
)

# ========================================
# CONFIGURATION CORS
# ========================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ========================================
# CRÉATION DES TABLES
# ========================================

models.Base.metadata.create_all(bind=engine)


# ========================================
# ÉVÉNEMENT DE DÉMARRAGE
# ========================================

@app.on_event("startup")
def startup_event():
    """Initialise la BD avec des données de test"""
    db = next(get_db())

    existing_institutions = crud.get_institutions(db, limit=1)

    if not existing_institutions:
        print("🔄 Initialisation de la base de données...")

        # Créer les institutions (comme avant)
        test_institutions = [
            # HÔPITAUX
            {"name": "Hôpital Aristide Le Dantec", "type": models.InstitutionType.HOSPITAL, "location": "Dakar", "address": "Avenue Pasteur, Dakar", "phone": "+221 33 821 21 81"},
            {"name": "Hôpital Principal de Dakar", "type": models.InstitutionType.HOSPITAL, "location": "Dakar", "address": "Avenue Nelson Mandela, Dakar", "phone": "+221 33 839 50 50"},
            {"name": "Hôpital Fann", "type": models.InstitutionType.HOSPITAL, "location": "Dakar", "address": "Route de Fann, Dakar", "phone": "+221 33 869 11 61"},
            {"name": "Hôpital Abass Ndao", "type": models.InstitutionType.HOSPITAL, "location": "Dakar", "address": "Point E, Dakar", "phone": "+221 33 824 06 42"},
            {"name": "Clinique Cheikh Zaid", "type": models.InstitutionType.HOSPITAL, "location": "Dakar", "address": "Guédiawaye, Dakar", "phone": "+221 33 835 23 80"},
            # MAIRIES
            {"name": "Mairie de Dakar", "type": models.InstitutionType.MAIRIE, "location": "Dakar", "address": "Place de l'Indépendance, Dakar", "phone": "+221 33 849 11 20"},
            {"name": "Mairie de Pikine", "type": models.InstitutionType.MAIRIE, "location": "Pikine", "address": "Centre-ville Pikine", "phone": "+221 33 834 03 03"},
            {"name": "Mairie de Guédiawaye", "type": models.InstitutionType.MAIRIE, "location": "Guédiawaye", "address": "Guédiawaye Centre", "phone": "+221 33 835 50 50"},
            # BANQUES
            {"name": "SGBS (Société Générale)", "type": models.InstitutionType.BANQUE, "location": "Dakar", "address": "Avenue Léopold Sédar Senghor, Dakar", "phone": "+221 33 839 93 93"},
            {"name": "BOA Sénégal", "type": models.InstitutionType.BANQUE, "location": "Dakar", "address": "Place de l'Indépendance, Dakar", "phone": "+221 33 849 13 13"},
            # TRANSPORTS
            {"name": "Gare Routière de Dakar", "type": models.InstitutionType.TRANSPORT, "location": "Dakar", "address": "Colobane, Dakar", "phone": "+221 33 822 05 05"},
            {"name": "Gare Routière Pompiers", "type": models.InstitutionType.TRANSPORT, "location": "Dakar", "address": "HLM Grand Yoff, Dakar", "phone": "+221 33 827 22 22"}
        ]

        for inst_data in test_institutions:
            inst_schema = schemas.InstitutionCreate(**inst_data)
            crud.create_institution(db, inst_schema)

        print("✅ Institutions créées")

        # Créer un admin par défaut
        try:
            admin_user = schemas.UserCreate(
                name="Admin QueueFlow",
                email="admin@queueflow.sn",
                password="admin123",
                role=models.UserRole.ADMIN
            )
            crud_users.create_user(db, admin_user)
            print("✅ Admin créé : admin@queueflow.sn / admin123")
        except:
            pass

        # Créer un opérateur de test
        try:
            operator_user = schemas.UserCreate(
                name="Dr. Amadou Diop",
                email="operator@hopital.sn",
                password="operator123",
                role=models.UserRole.OPERATOR,
                institution_id=1  # Hôpital Aristide Le Dantec
            )
            crud_users.create_user(db, operator_user)
            print("✅ Opérateur créé : operator@hopital.sn / operator123")
        except:
            pass

        print("✅ Base de données initialisée!")
    else:
        print("✅ Base de données déjà initialisée")


# ========================================
# ROUTE RACINE
# ========================================

@app.get("/", tags=["Root"])
def root():
    return {
        "message": "Bienvenue sur QueueFlow API Extended",
        "version": "2.0.0",
        "features": ["auth", "multi-roles", "tickets", "queues"],
        "documentation": "/docs"
    }


# ========================================
# ROUTES D'AUTHENTIFICATION
# ========================================

@app.post("/auth/signup", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED, tags=["Auth"])
def signup(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """
    Créer un nouveau compte utilisateur

    Par défaut, le rôle est "citizen"
    """
    try:
        db_user = crud_users.create_user(db, user)
        return db_user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@app.post("/auth/login", response_model=schemas.UserWithToken, tags=["Auth"])
def login(credentials: schemas.UserLogin, db: Session = Depends(get_db)):
    """
    Se connecter avec email et mot de passe

    Retourne les informations utilisateur
    """
    user = crud_users.authenticate_user(db, credentials.email, credentials.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou mot de passe incorrect"
        )

    return {
        **schemas.UserResponse.from_orm(user).dict(),
        "token": "session_active"
    }


@app.get("/auth/me", response_model=schemas.UserResponse, tags=["Auth"])
def get_current_user(user_id: int, db: Session = Depends(get_db)):
    """
    Récupère les informations de l'utilisateur connecté

    En production, user_id serait extrait du token JWT
    """
    user = crud_users.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utilisateur non trouvé"
        )
    return user


# ========================================
# ROUTES POUR LES INSTITUTIONS (existantes)
# ========================================

@app.get("/institutions", response_model=List[schemas.InstitutionResponse], tags=["Institutions"])
def list_institutions(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Liste toutes les institutions"""
    institutions = crud.get_institutions(db, skip=skip, limit=limit)
    return institutions


@app.get("/institutions/type/{institution_type}", response_model=List[schemas.InstitutionResponse], tags=["Institutions"])
def list_institutions_by_type(institution_type: models.InstitutionType, db: Session = Depends(get_db)):
    """Liste les institutions par type"""
    institutions = crud.get_institutions_by_type(db, institution_type)
    return institutions


@app.get("/institutions/{institution_id}", response_model=schemas.InstitutionResponse, tags=["Institutions"])
def get_institution(institution_id: int, db: Session = Depends(get_db)):
    """Récupère une institution par ID"""
    institution = crud.get_institution_by_id(db, institution_id)
    if institution is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Institution {institution_id} non trouvée"
        )
    return institution


# ========================================
# ROUTES POUR LES TICKETS (étendues)
# ========================================

@app.post("/tickets", response_model=schemas.TicketStats, status_code=status.HTTP_201_CREATED, tags=["Tickets"])
def create_new_ticket(ticket: schemas.TicketCreate, db: Session = Depends(get_db)):
    """
    Créer un nouveau ticket

    Si user_id est fourni, le ticket est lié à l'utilisateur
    """
    try:
        db_ticket = crud.create_ticket(db, ticket)
        ticket_stats = crud.get_ticket_stats(db, db_ticket.ticket_number)
        return ticket_stats
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@app.get("/tickets/{ticket_number}", response_model=schemas.TicketResponse, tags=["Tickets"])
def get_ticket_info(ticket_number: str, db: Session = Depends(get_db)):
    """Récupère les informations complètes d'un ticket"""
    ticket = crud.get_ticket_by_number(db, ticket_number)
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ticket {ticket_number} non trouvé"
        )
    return ticket


@app.get("/tickets/{ticket_number}/stats", response_model=schemas.TicketStats, tags=["Tickets"])
def get_ticket_statistics(ticket_number: str, db: Session = Depends(get_db)):
    """Récupère les statistiques d'un ticket"""
    ticket_stats = crud.get_ticket_stats(db, ticket_number)
    if not ticket_stats:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ticket {ticket_number} non trouvé"
        )
    return ticket_stats


@app.get("/users/{user_id}/tickets", response_model=List[schemas.TicketResponse], tags=["Tickets"])
def get_user_tickets(user_id: int, db: Session = Depends(get_db)):
    """Récupère l'historique des tickets d'un utilisateur"""
    tickets = crud_users.get_user_ticket_history(db, user_id)
    return tickets


# ========================================
# ROUTES POUR LES OPÉRATEURS
# ========================================

@app.post("/operator/next-ticket", response_model=schemas.NextTicketResponse, tags=["Operator"])
def call_next_ticket_route(institution_id: int, operator_id: int, db: Session = Depends(get_db)):
    """
    Appelle le prochain ticket en attente

    Utilisé par les opérateurs pour appeler les patients/clients
    """
    ticket = crud_users.call_next_ticket(db, institution_id, operator_id)

    if not ticket:
        return {
            "ticket": None,
            "message": "Aucun ticket en attente"
        }

    return {
        "ticket": ticket,
        "message": f"Ticket {ticket.ticket_number} appelé"
    }


@app.put("/operator/complete-ticket/{ticket_number}", response_model=schemas.TicketResponse, tags=["Operator"])
def complete_ticket_route(ticket_number: str, operator_id: int, db: Session = Depends(get_db)):
    """Marque un ticket comme complété"""
    ticket = crud_users.complete_ticket(db, ticket_number, operator_id)

    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ticket {ticket_number} non trouvé"
        )

    return ticket


@app.put("/operator/miss-ticket/{ticket_number}", response_model=schemas.TicketResponse, tags=["Operator"])
def miss_ticket_route(ticket_number: str, db: Session = Depends(get_db)):
    """Marque un ticket comme manqué"""
    ticket = crud_users.mark_ticket_missed(db, ticket_number)

    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ticket {ticket_number} non trouvé"
        )

    return ticket


@app.get("/operator/{operator_id}/stats", response_model=schemas.OperatorStats, tags=["Operator"])
def get_operator_statistics(operator_id: int, db: Session = Depends(get_db)):
    """Récupère les statistiques d'un opérateur"""
    operator = crud_users.get_user_by_id(db, operator_id)
    if not operator:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Opérateur non trouvé"
        )

    stats = crud_users.get_operator_stats(db, operator_id)

    return {
        "user_id": operator_id,
        "name": operator.name,
        "tickets_served_today": stats["tickets_served_today"],
        "average_service_time": 3,
        "current_ticket": stats["current_ticket"]
    }


# ========================================
# ROUTES POUR LES ADMINISTRATEURS
# ========================================

@app.get("/admin/stats", response_model=schemas.AdminStats, tags=["Admin"])
def get_admin_statistics(db: Session = Depends(get_db)):
    """Récupère les statistiques globales du système"""
    stats = crud_users.get_admin_stats(db)
    return stats


@app.get("/admin/operators", response_model=List[schemas.UserResponse], tags=["Admin"])
def list_operators(db: Session = Depends(get_db)):
    """Liste tous les opérateurs"""
    operators = crud_users.get_all_operators(db)
    return operators


@app.get("/admin/institutions/{institution_id}/operators", response_model=List[schemas.UserResponse], tags=["Admin"])
def list_institution_operators(institution_id: int, db: Session = Depends(get_db)):
    """Liste les opérateurs d'une institution"""
    operators = crud_users.get_operators_by_institution(db, institution_id)
    return operators


# ========================================
# ROUTES POUR LES QUEUES
# ========================================

@app.get("/queue/{institution_id}", response_model=schemas.QueueInfo, tags=["Queues"])
def get_institution_queue_info(institution_id: int, db: Session = Depends(get_db)):
    """Récupère les informations de la file d'attente"""
    institution = crud.get_institution_by_id(db, institution_id)
    if not institution:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Institution {institution_id} non trouvée"
        )

    queue_info = crud.get_queue_info(db, institution_id)
    if not queue_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"File d'attente non trouvée"
        )

    return queue_info


@app.get("/queue/details/{institution_id}", response_model=schemas.QueueResponse, tags=["Queues"])
def get_queue_details(institution_id: int, db: Session = Depends(get_db)):
    """Récupère les détails complets de la queue"""
    queue = crud.get_queue_by_institution(db, institution_id)
    if not queue:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Queue non trouvée"
        )
    return queue


# ========================================
# HEALTH & STATS
# ========================================

@app.get("/health", tags=["Health"])
def health_check():
    """Vérifie que l'API fonctionne"""
    return {
        "status": "healthy",
        "service": "QueueFlow API Extended",
        "version": "2.0.0"
    }
