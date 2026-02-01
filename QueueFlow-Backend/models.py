from sqlalchemy import Column, Integer, String, ForeignKey, Date, DateTime
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    name = Column(String)
    role = Column(String)  # citizen, operator, admin
    institution_id = Column(Integer, ForeignKey("institutions.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relations
    tickets = relationship("Ticket", back_populates="user")
    institution = relationship("Institution", back_populates="users")

class Institution(Base):
    __tablename__ = "institutions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    city = Column(String)
    type = Column(String)  # Hôpital, Mairie, Banque, Transport

    # Relations
    services = relationship("Service", back_populates="institution")
    tickets = relationship("Ticket", back_populates="institution")
    users = relationship("User", back_populates="institution")

class Service(Base):
    __tablename__ = "services"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    institution_id = Column(Integer, ForeignKey("institutions.id"))
    avg_time = Column(Integer)  # Temps moyen en minutes

    # Relations
    institution = relationship("Institution", back_populates="services")
    tickets = relationship("Ticket", back_populates="service")

class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, index=True)
    ticket_number = Column(String)
    user_id = Column(Integer, ForeignKey("users.id"))
    institution_id = Column(Integer, ForeignKey("institutions.id"))
    service_id = Column(Integer, ForeignKey("services.id"))
    scheduled_time = Column(String)
    date = Column(Date)
    status = Column(String, default="waiting")  # waiting, beingtreated, treated, missed
    position = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relations
    user = relationship("User", back_populates="tickets")
    institution = relationship("Institution", back_populates="tickets")
    service = relationship("Service", back_populates="tickets")
