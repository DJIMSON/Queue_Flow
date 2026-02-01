from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
import jwt
from passlib.context import CryptContext
import os

from database import get_db, engine, Base
from models import User, Institution, Service, Ticket
from pydantic import BaseModel, EmailStr

# Créer les tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="QueueFlow API",
    description="API de gestion de files d'attente",
    version="1.0.0"
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En production, spécifier les domaines autorisés
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Sécurité
SECRET_KEY = os.getenv("SECRET_KEY", "votre-secret-key-super-securisee-changez-moi")
ALGORITHM = "HS256"
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

# ============================================
# SCHEMAS PYDANTIC
# ============================================

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    name: str
    role: str = "citizen"
    institution_id: Optional[int] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: dict

class TicketCreate(BaseModel):
    institution_id: int
    service_id: int
    scheduled_time: str

class TicketUpdate(BaseModel):
    status: str

# ============================================
# FONCTIONS UTILITAIRES
# ============================================

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=7)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Token invalide")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expiré")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Token invalide")

    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise HTTPException(status_code=401, detail="Utilisateur non trouvé")
    return user

# ============================================
# ROUTES AUTHENTIFICATION
# ============================================

@app.post("/api/auth/signup", response_model=TokenResponse)
def signup(user_data: UserCreate, db: Session = Depends(get_db)):
    # Vérifier si l'email existe déjà
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email déjà utilisé")

    # Créer le nouvel utilisateur
    hashed_password = get_password_hash(user_data.password)
    new_user = User(
        email=user_data.email,
        password=hashed_password,
        name=user_data.name,
        role=user_data.role,
        institution_id=user_data.institution_id
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Créer le token
    access_token = create_access_token(data={"sub": new_user.email})

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": new_user.id,
            "email": new_user.email,
            "name": new_user.name,
            "role": new_user.role,
            "institution_id": new_user.institution_id
        }
    }

@app.post("/api/auth/login", response_model=TokenResponse)
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == credentials.email).first()

    if not user or not verify_password(credentials.password, user.password):
        raise HTTPException(status_code=401, detail="Email ou mot de passe incorrect")

    access_token = create_access_token(data={"sub": user.email})

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "role": user.role,
            "institution_id": user.institution_id
        }
    }

@app.get("/api/auth/me")
def get_me(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "email": current_user.email,
        "name": current_user.name,
        "role": current_user.role,
        "institution_id": current_user.institution_id
    }

# ============================================
# ROUTES INSTITUTIONS
# ============================================

@app.get("/api/institutions")
def get_institutions(db: Session = Depends(get_db)):
    institutions = db.query(Institution).all()
    return institutions

@app.get("/api/institutions/{institution_id}")
def get_institution(institution_id: int, db: Session = Depends(get_db)):
    institution = db.query(Institution).filter(Institution.id == institution_id).first()
    if not institution:
        raise HTTPException(status_code=404, detail="Institution non trouvée")
    return institution

# ============================================
# ROUTES SERVICES
# ============================================

@app.get("/api/services")
def get_services(institution_id: Optional[int] = None, db: Session = Depends(get_db)):
    query = db.query(Service)
    if institution_id:
        query = query.filter(Service.institution_id == institution_id)
    services = query.all()
    return services

# ============================================
# ROUTES TICKETS
# ============================================

@app.post("/api/tickets")
def create_ticket(ticket_data: TicketCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Vérifier que le service existe
    service = db.query(Service).filter(Service.id == ticket_data.service_id).first()
    if not service:
        raise HTTPException(status_code=404, detail="Service non trouvé")

    # Compter les tickets du jour pour ce service
    today = datetime.now().date()
    tickets_today = db.query(Ticket).filter(
        Ticket.service_id == ticket_data.service_id,
        Ticket.date == today
    ).count()

    # Créer le ticket
    new_ticket = Ticket(
        user_id=current_user.id,
        institution_id=ticket_data.institution_id,
        service_id=ticket_data.service_id,
        scheduled_time=ticket_data.scheduled_time,
        date=today,
        status="waiting",
        position=tickets_today + 1,
        ticket_number=f"{tickets_today + 1:05d}"
    )

    db.add(new_ticket)
    db.commit()
    db.refresh(new_ticket)

    return new_ticket

@app.get("/api/tickets")
def get_tickets(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role == "citizen":
        tickets = db.query(Ticket).filter(Ticket.user_id == current_user.id).all()
    elif current_user.role == "operator":
        today = datetime.now().date()
        tickets = db.query(Ticket).filter(
            Ticket.institution_id == current_user.institution_id,
            Ticket.date == today
        ).all()
    elif current_user.role == "admin":
        tickets = db.query(Ticket).all()
    else:
        tickets = []

    return tickets

@app.get("/api/tickets/{ticket_id}")
def get_ticket(ticket_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()

    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket non trouvé")

    # Vérifier les permissions
    if current_user.role == "citizen" and ticket.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Accès refusé")

    return ticket

@app.patch("/api/tickets/{ticket_id}")
def update_ticket(
    ticket_id: int,
    ticket_update: TicketUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()

    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket non trouvé")

    # Seul un opérateur ou admin peut modifier le statut
    if current_user.role not in ["operator", "admin"]:
        raise HTTPException(status_code=403, detail="Accès refusé")

    ticket.status = ticket_update.status
    db.commit()
    db.refresh(ticket)

    return ticket

@app.delete("/api/tickets/{ticket_id}")
def delete_ticket(
    ticket_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()

    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket non trouvé")

    # Vérifier les permissions
    if current_user.role == "citizen" and ticket.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Accès refusé")

    db.delete(ticket)
    db.commit()

    return {"message": "Ticket supprimé"}

# ============================================
# ROUTE DE TEST
# ============================================

@app.get("/")
def root():
    return {
        "message": "QueueFlow API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}

# ============================================
# INITIALISER LES DONNÉES DE TEST
# ============================================

@app.on_event("startup")
def startup_event():
    db = next(get_db())

    # Vérifier si des institutions existent déjà
    if db.query(Institution).count() == 0:
        # Créer les institutions de test
        institutions_data = [
            {"name": "Hôpital Aristide Le Dantec", "city": "Dakar", "type": "Hôpital"},
            {"name": "Hôpital Principal de Dakar", "city": "Dakar", "type": "Hôpital"},
            {"name": "Hôpital Fann", "city": "Dakar", "type": "Hôpital"},
            {"name": "Mairie Plateau", "city": "Dakar", "type": "Mairie"},
            {"name": "Banque BICIS", "city": "Dakar", "type": "Banque"},
        ]

        for inst_data in institutions_data:
            institution = Institution(**inst_data)
            db.add(institution)

        db.commit()

        # Créer les services de test
        services_data = [
            {"name": "Consultations Générales", "institution_id": 1, "avg_time": 15},
            {"name": "Urgences", "institution_id": 1, "avg_time": 20},
            {"name": "Cardiologie", "institution_id": 1, "avg_time": 25},
            {"name": "État Civil", "institution_id": 4, "avg_time": 10},
            {"name": "Ouverture de Compte", "institution_id": 5, "avg_time": 20},
        ]

        for svc_data in services_data:
            service = Service(**svc_data)
            db.add(service)

        db.commit()

        print("✅ Données de test initialisées")
