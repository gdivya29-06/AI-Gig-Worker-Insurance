from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from jose import JWTError, jwt
from datetime import datetime, timedelta
from database import get_db, Worker
import hashlib

router = APIRouter(prefix="/auth", tags=["Auth"])

SECRET_KEY = "gig_insurance_secret_key_2024"
ALGORITHM  = "HS256"
TOKEN_EXPIRE_HOURS = 24

# ── Schemas ──────────────────────────────────────────────────

class RegisterRequest(BaseModel):
    name: str
    phone: str
    email: str
    password: str
    city: str
    zone: str
    platform: str               # Zomato or Swiggy
    avg_daily_orders: float = 20
    avg_daily_income: float = 600
    experience_years: float = 1

class LoginRequest(BaseModel):
    phone: str
    password: str

# ── Helpers ──────────────────────────────────────────────────

def hash_password(password: str) -> str:
    """Simple SHA256 hashing — works on all Python versions"""
    salt = "gig_shield_salt_2024"
    return hashlib.sha256(f"{salt}{password}".encode()).hexdigest()

def verify_password(plain: str, hashed: str) -> bool:
    return hash_password(plain) == hashed

def create_token(data: dict) -> str:
    payload = data.copy()
    payload["exp"] = datetime.utcnow() + timedelta(hours=TOKEN_EXPIRE_HOURS)
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

# ── Routes ───────────────────────────────────────────────────

@router.post("/register")
def register(req: RegisterRequest, db: Session = Depends(get_db)):
    if db.query(Worker).filter(Worker.phone == req.phone).first():
        raise HTTPException(status_code=400, detail="Phone number already registered")
    if db.query(Worker).filter(Worker.email == req.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    worker = Worker(
        name             = req.name,
        phone            = req.phone,
        email            = req.email,
        password_hash    = hash_password(req.password),
        city             = req.city,
        zone             = req.zone,
        platform         = req.platform,
        avg_daily_orders = req.avg_daily_orders,
        avg_daily_income = req.avg_daily_income,
        experience_years = req.experience_years,
    )
    db.add(worker)
    db.commit()
    db.refresh(worker)

    token = create_token({"worker_id": worker.id, "phone": worker.phone})
    return {
        "message": "Registration successful",
        "worker_id": worker.id,
        "token": token,
        "worker": {
            "name": worker.name,
            "city": worker.city,
            "zone": worker.zone,
            "platform": worker.platform,
        }
    }

@router.post("/login")
def login(req: LoginRequest, db: Session = Depends(get_db)):
    worker = db.query(Worker).filter(Worker.phone == req.phone).first()
    if not worker or not verify_password(req.password, worker.password_hash):
        raise HTTPException(status_code=401, detail="Invalid phone or password")

    token = create_token({"worker_id": worker.id, "phone": worker.phone})
    return {
        "message": "Login successful",
        "worker_id": worker.id,
        "token": token,
        "worker": {
            "name": worker.name,
            "city": worker.city,
            "zone": worker.zone,
            "platform": worker.platform,
            "avg_daily_income": worker.avg_daily_income,
        }
    }

@router.get("/worker/{worker_id}")
def get_worker(worker_id: int, db: Session = Depends(get_db)):
    worker = db.query(Worker).filter(Worker.id == worker_id).first()
    if not worker:
        raise HTTPException(status_code=404, detail="Worker not found")
    return {
        "id": worker.id,
        "name": worker.name,
        "phone": worker.phone,
        "email": worker.email,
        "city": worker.city,
        "zone": worker.zone,
        "platform": worker.platform,
        "avg_daily_orders": worker.avg_daily_orders,
        "avg_daily_income": worker.avg_daily_income,
        "experience_years": worker.experience_years,
        "created_at": worker.created_at,
    }