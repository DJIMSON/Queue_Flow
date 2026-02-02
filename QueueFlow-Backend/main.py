from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel, EmailStr
from datetime import datetime, timedelta
from typing import Optional, List
import jwt
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

# Configuration
DATABASE_URL = "sqlite:///./queueflow.db"
SECRET_KEY = "votre_cle_secrete_super_securisee_changez_moi_en_production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Database setup
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Password hasher
pwd_hasher = PasswordHasher()

# Models
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(String, default="user")
    institution_id = Column(Integer, ForeignKey("institutions.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Institution(Base):
    __tablename__ = "institutions"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    type = Column(String)
    address = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

class Service(Base):
    __tablename__ = "services"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    institution_id = Column(Integer, ForeignKey("institutions.id"))
    estimated_time = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)

class Ticket(Base):
    __tablename__ = "tickets"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    institution_id = Column(Integer, ForeignKey("institutions.id"))
    service_id = Column(Integer, ForeignKey("services.id"))
    ticket_number = Column(String)
    status = Column(String, default="waiting")
    scheduled_time = Column(String)
    position = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)

# Create tables
Base.metadata.create_all(bind=engine)

# Pydantic schemas
class UserCreate(BaseModel):
    full_name: str
    email: EmailStr
    password: str
    role: str = "user"
    institution_id: Optional[int] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class InstitutionCreate(BaseModel):
    name: str
    type: str
    address: str

class ServiceCreate(BaseModel):
    name: str
    institution_id: int
    estimated_time: int

class TicketCreate(BaseModel):
    institution_id: int
    service_id: int
    scheduled_time: str

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Password functions
def verify_password(plain_password, hashed_password):
    try:
        pwd_hasher.verify(hashed_password, plain_password)
        return True
    except VerifyMismatchError:
        return False

def get_password_hash(password):
    return pwd_hasher.hash(password)

# JWT functions
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(token: str, db: Session):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = int(payload.get("sub"))
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=401, detail="Utilisateur non trouvé")
        return user
    except:
        raise HTTPException(status_code=401, detail="Token invalide")

def check_role(token: str, required_roles: list, db: Session):
    user = get_current_user(token, db)
    if user.role not in required_roles:
        raise HTTPException(status_code=403, detail="Accès refusé")
    return user

# FastAPI app
app = FastAPI(title="QueueFlow API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize test data
@app.on_event("startup")
def init_test_data():
    db = SessionLocal()

    # Vérifier si les données existent déjà
    if db.query(Institution).count() > 0:
        db.close()
        return

    # Créer des institutions
    institutions = [
        Institution(name="Hôpital Le Dantec", type="Hôpitaux", address="Avenue Pasteur, Dakar"),
        Institution(name="Hôpital Principal", type="Hôpitaux", address="Plateau, Dakar"),
        Institution(name="Banque Atlantique", type="Banques", address="Place de l'Indépendance"),
        Institution(name="SGBS", type="Banques", address="Boulevard Djily Mbaye"),
        Institution(name="Mairie de Dakar", type="Administrations", address="Plateau, Dakar"),
    ]

    for inst in institutions:
        db.add(inst)
    db.commit()

    # Créer des services
    services = [
        Service(name="Consultations Générales", institution_id=1, estimated_time=30),
        Service(name="Urgences", institution_id=1, estimated_time=15),
        Service(name="Analyses Médicales", institution_id=1, estimated_time=20),
        Service(name="Consultations", institution_id=2, estimated_time=30),
        Service(name="Radiologie", institution_id=2, estimated_time=25),
        Service(name="Ouverture de Compte", institution_id=3, estimated_time=20),
        Service(name="Retrait/Dépôt", institution_id=3, estimated_time=10),
        Service(name="Services Bancaires", institution_id=4, estimated_time=15),
        Service(name="État Civil", institution_id=5, estimated_time=25),
        Service(name="Urbanisme", institution_id=5, estimated_time=30),
    ]

    for service in services:
        db.add(service)
    db.commit()

    # Créer un admin
    admin = User(
        full_name="Admin Principal",
        email="admin@queueflow.com",
        hashed_password=get_password_hash("admin123"),
        role="admin"
    )
    db.add(admin)

    # Créer des opérateurs pour chaque institution
    operators = [
        User(
            full_name="Opérateur Le Dantec",
            email="operator@ledantec.sn",
            hashed_password=get_password_hash("operator123"),
            role="operator",
            institution_id=1
        ),
        User(
            full_name="Opérateur Hôpital Principal",
            email="operator@principal.sn",
            hashed_password=get_password_hash("operator123"),
            role="operator",
            institution_id=2
        ),
        User(
            full_name="Opérateur Banque Atlantique",
            email="operator@atlantique.sn",
            hashed_password=get_password_hash("operator123"),
            role="operator",
            institution_id=3
        ),
    ]

    for op in operators:
        db.add(op)

    db.commit()
    db.close()

    print("✅ Données de test initialisées")
    print("📧 Admin: admin@queueflow.com / admin123")
    print("📧 Opérateur Le Dantec: operator@ledantec.sn / operator123")

# Routes - Authentication
@app.post("/api/auth/signup")
def signup(user_data: UserCreate, db: Session = Depends(get_db)):
    # Vérifier si l'utilisateur existe
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email déjà utilisé")

    # Hasher le mot de passe
    hashed_password = get_password_hash(user_data.password)

    # Créer l'utilisateur
    new_user = User(
        full_name=user_data.full_name,
        email=user_data.email,
        hashed_password=hashed_password,
        role=user_data.role,
        institution_id=user_data.institution_id
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Créer le token
    token = create_access_token(data={"sub": str(new_user.id)})

    return {
        "token": token,
        "user": {
            "id": new_user.id,
            "full_name": new_user.full_name,
            "email": new_user.email,
            "role": new_user.role,
            "institution_id": new_user.institution_id
        }
    }

@app.post("/api/auth/login")
def login(user_data: UserLogin, db: Session = Depends(get_db)):
    # Chercher l'utilisateur
    user = db.query(User).filter(User.email == user_data.email).first()

    if not user or not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Email ou mot de passe incorrect")

    # Créer le token
    token = create_access_token(data={"sub": str(user.id)})

    return {
        "token": token,
        "user": {
            "id": user.id,
            "full_name": user.full_name,
            "email": user.email,
            "role": user.role,
            "institution_id": user.institution_id
        }
    }

# Routes - Institutions
@app.get("/api/institutions")
def get_institutions(db: Session = Depends(get_db)):
    institutions = db.query(Institution).all()
    return [{
        "id": inst.id,
        "name": inst.name,
        "type": inst.type,
        "address": inst.address
    } for inst in institutions]

@app.post("/api/institutions")
def create_institution(institution: InstitutionCreate, db: Session = Depends(get_db)):
    new_institution = Institution(**institution.dict())
    db.add(new_institution)
    db.commit()
    db.refresh(new_institution)
    return {
        "id": new_institution.id,
        "name": new_institution.name,
        "type": new_institution.type,
        "address": new_institution.address
    }

@app.get("/api/institutions/types")
def get_institution_types(db: Session = Depends(get_db)):
    types = db.query(Institution.type).distinct().all()
    return [t[0] for t in types]

# Routes - Services
@app.get("/api/services")
def get_services(institution_id: Optional[int] = None, db: Session = Depends(get_db)):
    query = db.query(Service)
    if institution_id:
        query = query.filter(Service.institution_id == institution_id)
    services = query.all()
    return [{
        "id": s.id,
        "name": s.name,
        "institution_id": s.institution_id,
        "estimated_time": s.estimated_time
    } for s in services]

@app.post("/api/services")
def create_service(service: ServiceCreate, db: Session = Depends(get_db)):
    new_service = Service(**service.dict())
    db.add(new_service)
    db.commit()
    db.refresh(new_service)
    return {
        "id": new_service.id,
        "name": new_service.name,
        "institution_id": new_service.institution_id,
        "estimated_time": new_service.estimated_time
    }

# Routes - Tickets
@app.get("/api/tickets")
def get_tickets(
    user_id: Optional[int] = None,
    institution_id: Optional[int] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Ticket)

    if user_id:
        query = query.filter(Ticket.user_id == user_id)
    if institution_id:
        query = query.filter(Ticket.institution_id == institution_id)
    if status:
        query = query.filter(Ticket.status == status)

    tickets = query.order_by(Ticket.created_at.desc()).all()

    result = []
    for ticket in tickets:
        institution = db.query(Institution).filter(Institution.id == ticket.institution_id).first()
        service = db.query(Service).filter(Service.id == ticket.service_id).first()
        user = db.query(User).filter(User.id == ticket.user_id).first()

        result.append({
            "id": ticket.id,
            "ticket_number": ticket.ticket_number,
            "status": ticket.status,
            "scheduled_time": ticket.scheduled_time,
            "position": ticket.position,
            "created_at": ticket.created_at.isoformat(),
            "institution": {
                "id": institution.id,
                "name": institution.name
            } if institution else None,
            "service": {
                "id": service.id,
                "name": service.name
            } if service else None,
            "user": {
                "id": user.id,
                "full_name": user.full_name
            } if user else None
        })

    return result

@app.post("/api/tickets")
def create_ticket(ticket_data: TicketCreate, user_id: int, db: Session = Depends(get_db)):
    # Générer le numéro de ticket
    today = datetime.now().date()
    today_tickets = db.query(Ticket).filter(
        Ticket.institution_id == ticket_data.institution_id,
        Ticket.service_id == ticket_data.service_id
    ).count()

    ticket_number = f"T{today_tickets + 1:04d}"

    # Calculer la position dans la file
    waiting_tickets = db.query(Ticket).filter(
        Ticket.institution_id == ticket_data.institution_id,
        Ticket.service_id == ticket_data.service_id,
        Ticket.status == "waiting"
    ).count()

    position = waiting_tickets + 1

    # Créer le ticket
    new_ticket = Ticket(
        user_id=user_id,
        institution_id=ticket_data.institution_id,
        service_id=ticket_data.service_id,
        ticket_number=ticket_number,
        status="waiting",
        scheduled_time=ticket_data.scheduled_time,
        position=position
    )

    db.add(new_ticket)
    db.commit()
    db.refresh(new_ticket)

    institution = db.query(Institution).filter(Institution.id == new_ticket.institution_id).first()
    service = db.query(Service).filter(Service.id == new_ticket.service_id).first()

    return {
        "id": new_ticket.id,
        "ticket_number": new_ticket.ticket_number,
        "status": new_ticket.status,
        "scheduled_time": new_ticket.scheduled_time,
        "position": new_ticket.position,
        "created_at": new_ticket.created_at.isoformat(),
        "institution": {
            "id": institution.id,
            "name": institution.name
        },
        "service": {
            "id": service.id,
            "name": service.name,
            "estimated_time": service.estimated_time
        }
    }

@app.put("/api/tickets/{ticket_id}/cancel")
def cancel_ticket(ticket_id: int, db: Session = Depends(get_db)):
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()

    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket non trouvé")

    ticket.status = "cancelled"
    db.commit()

    return {"message": "Ticket annulé avec succès"}

@app.put("/api/tickets/{ticket_id}/call")
def call_ticket(ticket_id: int, db: Session = Depends(get_db)):
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()

    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket non trouvé")

    ticket.status = "called"
    db.commit()

    return {"message": "Ticket appelé avec succès"}

@app.put("/api/tickets/{ticket_id}/complete")
def complete_ticket(ticket_id: int, db: Session = Depends(get_db)):
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()

    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket non trouvé")

    ticket.status = "completed"
    db.commit()

    # Mettre à jour les positions des autres tickets
    waiting_tickets = db.query(Ticket).filter(
        Ticket.institution_id == ticket.institution_id,
        Ticket.service_id == ticket.service_id,
        Ticket.status == "waiting",
        Ticket.position > ticket.position
    ).all()

    for t in waiting_tickets:
        t.position -= 1

    db.commit()

    return {"message": "Ticket complété avec succès"}

# Routes - Admin Stats
@app.get("/api/admin/stats")
def get_admin_stats(db: Session = Depends(get_db)):
    total_users = db.query(User).count()
    total_institutions = db.query(Institution).count()
    total_tickets = db.query(Ticket).count()
    active_tickets = db.query(Ticket).filter(Ticket.status == "waiting").count()

    return {
        "total_users": total_users,
        "total_institutions": total_institutions,
        "total_tickets": total_tickets,
        "active_tickets": active_tickets
    }

# Root
@app.get("/")
def root():
    return {
        "message": "QueueFlow API",
        "version": "1.0.0",
        "status": "running"
    }
