from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

DATABASE_URL = "sqlite:///./gig_insurance.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# ── Tables ──────────────────────────────────────────────────

class Worker(Base):
    __tablename__ = "workers"
    id            = Column(Integer, primary_key=True, index=True)
    name          = Column(String)
    phone         = Column(String, unique=True, index=True)
    email         = Column(String, unique=True)
    password_hash = Column(String)
    city          = Column(String)
    zone          = Column(String)          # e.g. "Koramangala", "Indiranagar"
    platform      = Column(String)          # Zomato / Swiggy
    avg_daily_orders = Column(Float, default=20)
    avg_daily_income = Column(Float, default=600)
    experience_years = Column(Float, default=1)
    created_at    = Column(DateTime, default=datetime.utcnow)

class Policy(Base):
    __tablename__ = "policies"
    id            = Column(Integer, primary_key=True, index=True)
    worker_id     = Column(Integer)
    weekly_premium = Column(Float)
    coverage_amount = Column(Float)
    risk_score    = Column(Float)
    status        = Column(String, default="active")   # active / expired / cancelled
    start_date    = Column(DateTime, default=datetime.utcnow)
    end_date      = Column(DateTime)
    city          = Column(String)
    zone          = Column(String)

class Claim(Base):
    __tablename__ = "claims"
    id            = Column(Integer, primary_key=True, index=True)
    worker_id     = Column(Integer)
    policy_id     = Column(Integer)
    trigger_type  = Column(String)          # heavy_rain / extreme_heat / poor_aqi / curfew
    trigger_value = Column(String)          # e.g. "rainfall: 45mm"
    claimed_amount = Column(Float)
    approved_amount = Column(Float, default=0)
    status        = Column(String, default="pending")  # pending / approved / rejected
    fraud_score   = Column(Float, default=0)
    fraud_reason  = Column(Text, default="")
    created_at    = Column(DateTime, default=datetime.utcnow)
    resolved_at   = Column(DateTime, nullable=True)

class Payout(Base):
    __tablename__ = "payouts"
    id            = Column(Integer, primary_key=True, index=True)
    claim_id      = Column(Integer)
    worker_id     = Column(Integer)
    amount        = Column(Float)
    method        = Column(String, default="UPI")
    status        = Column(String, default="processed")
    transaction_id = Column(String)
    processed_at  = Column(DateTime, default=datetime.utcnow)

class DisruptionLog(Base):
    __tablename__ = "disruption_logs"
    id            = Column(Integer, primary_key=True, index=True)
    city          = Column(String)
    disruption_type = Column(String)
    severity      = Column(String)          # low / medium / high
    raw_value     = Column(String)
    detected_at   = Column(DateTime, default=datetime.utcnow)

# ── Create all tables ────────────────────────────────────────

def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()