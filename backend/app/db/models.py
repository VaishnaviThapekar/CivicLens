from sqlalchemy import Column, String, Float, Integer, DateTime, Text, JSON, Boolean
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()

class UserModel(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True)
    full_name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    role = Column(String, nullable=False, default="Citizen")
    hashed_password = Column(String, nullable=True)
    karma_points = Column(Integer, default=100)
    created_at = Column(DateTime, default=datetime.utcnow)

class ComplaintModel(Base):
    __tablename__ = "complaints"

    id = Column(String, primary_key=True, index=True)
    unique_tracking_number = Column(String, unique=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String, nullable=False)
    priority = Column(String, default="P3 — Medium")
    status = Column(String, default="Submitted")
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    location_name = Column(String, nullable=True)
    image_url = Column(String, nullable=True)
    audio_url = Column(String, nullable=True)
    cluster_id = Column(String, nullable=True)
    assigned_officer_id = Column(String, nullable=True)
    assigned_team = Column(String, nullable=True)
    verification_result = Column(JSON, nullable=True)
    citizen_feedback = Column(JSON, nullable=True)
    created_by_email = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class AuditLogModel(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    complaint_id = Column(String, nullable=False, index=True)
    actor_email = Column(String, nullable=False)
    action = Column(String, nullable=False)
    details = Column(JSON, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

class ContractorModel(Base):
    __tablename__ = "contractors"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    category = Column(String, nullable=False)
    sla_compliance_rate = Column(Float, default=95.0)
    quality_rating = Column(Float, default=4.5)
    active_assignments = Column(Integer, default=0)
