from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime, timedelta

from database import init_db, get_db, Policy, Claim, Worker
from auth import router as auth_router
from dashboard import router as dashboard_router
from premium_calculator import calculate_weekly_premium
from claims_engine import initiate_claim, auto_trigger_claims
from weather import detect_disruptions

# ── App setup ─────────────────────────────────────────────────
app = FastAPI(
    title="GigShield — AI Insurance for Food Delivery Workers",
    description="Parametric income insurance for Zomato/Swiggy delivery partners",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # In production, replace with frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Init DB on startup ────────────────────────────────────────
@app.on_event("startup")
def startup():
    init_db()
    print("✅ Database initialized")

# ── Include routers ───────────────────────────────────────────
app.include_router(auth_router)
app.include_router(dashboard_router)

# ── Premium endpoints ─────────────────────────────────────────

class PremiumRequest(BaseModel):
    city: str
    zone: str
    experience_years: float = 1.0
    avg_daily_income: float = 600.0
    platform: str = "zomato"
    tier: str = "standard"

@app.post("/premium/calculate")
def get_premium(req: PremiumRequest):
    result = calculate_weekly_premium(
        city             = req.city,
        zone             = req.zone,
        experience_years = req.experience_years,
        avg_daily_income = req.avg_daily_income,
        platform         = req.platform,
        tier             = req.tier,
    )
    return result

# ── Policy endpoints ──────────────────────────────────────────

class PolicyRequest(BaseModel):
    worker_id: int
    tier: str = "standard"

@app.post("/policy/create")
def create_policy(req: PolicyRequest, db: Session = Depends(get_db)):
    worker = db.query(Worker).filter(Worker.id == req.worker_id).first()
    if not worker:
        raise HTTPException(status_code=404, detail="Worker not found")

    # Check for existing active policy
    now = datetime.utcnow()
    existing = db.query(Policy).filter(
        Policy.worker_id == req.worker_id,
        Policy.status == "active",
        Policy.end_date >= now
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Worker already has an active policy")

    premium_data = calculate_weekly_premium(
        city             = worker.city,
        zone             = worker.zone,
        experience_years = worker.experience_years,
        avg_daily_income = worker.avg_daily_income,
        platform         = worker.platform,
        tier             = req.tier,
    )

    policy = Policy(
        worker_id       = worker.id,
        weekly_premium  = premium_data["weekly_premium"],
        coverage_amount = premium_data["coverage_amount"],
        risk_score      = premium_data["risk_score"],
        status          = "active",
        start_date      = now,
        end_date        = now + timedelta(days=7),
        city            = worker.city,
        zone            = worker.zone,
    )
    db.add(policy)
    db.commit()
    db.refresh(policy)

    return {
        "message":        "✅ Policy created successfully!",
        "policy_id":      policy.id,
        "weekly_premium": policy.weekly_premium,
        "coverage_amount": policy.coverage_amount,
        "valid_until":    policy.end_date.isoformat(),
        "risk_level":     premium_data["risk_level"],
        "tier":           premium_data["tier"],
    }

@app.get("/policy/active/{worker_id}")
def get_active_policy(worker_id: int, db: Session = Depends(get_db)):
    now = datetime.utcnow()
    policy = db.query(Policy).filter(
        Policy.worker_id == worker_id,
        Policy.status == "active",
        Policy.end_date >= now
    ).first()
    if not policy:
        return {"active_policy": None, "message": "No active policy found"}
    return {
        "policy_id":       policy.id,
        "weekly_premium":  policy.weekly_premium,
        "coverage_amount": policy.coverage_amount,
        "risk_score":      policy.risk_score,
        "start_date":      policy.start_date.isoformat(),
        "end_date":        policy.end_date.isoformat(),
        "days_remaining":  (policy.end_date - now).days,
        "status":          policy.status,
    }

# ── Claims endpoints ──────────────────────────────────────────

class ClaimRequest(BaseModel):
    worker_id: int
    trigger_type: str   # heavy_rain / extreme_heat / poor_aqi / flood_risk / curfew

@app.post("/claims/initiate")
def file_claim(req: ClaimRequest, db: Session = Depends(get_db)):
    return initiate_claim(req.worker_id, req.trigger_type, db)

@app.get("/claims/status/{claim_id}")
def claim_status(claim_id: int, db: Session = Depends(get_db)):
    claim = db.query(Claim).filter(Claim.id == claim_id).first()
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")
    return {
        "claim_id":       claim.id,
        "worker_id":      claim.worker_id,
        "trigger_type":   claim.trigger_type,
        "trigger_value":  claim.trigger_value,
        "claimed_amount": claim.claimed_amount,
        "approved_amount": claim.approved_amount,
        "status":         claim.status,
        "fraud_score":    claim.fraud_score,
        "created_at":     claim.created_at.isoformat(),
        "resolved_at":    claim.resolved_at.isoformat() if claim.resolved_at else None,
    }

@app.get("/claims/worker/{worker_id}")
def worker_claims(worker_id: int, db: Session = Depends(get_db)):
    claims = db.query(Claim).filter(
        Claim.worker_id == worker_id
    ).order_by(Claim.created_at.desc()).all()
    return {
        "worker_id": worker_id,
        "total":     len(claims),
        "claims": [
            {
                "claim_id":       c.id,
                "trigger_type":   c.trigger_type,
                "claimed_amount": c.claimed_amount,
                "approved_amount": c.approved_amount,
                "status":         c.status,
                "date":           c.created_at.isoformat(),
            }
            for c in claims
        ]
    }

# ── Weather / Trigger endpoints ───────────────────────────────

@app.get("/triggers/check/{city}")
def check_triggers(city: str):
    return detect_disruptions(city)

@app.post("/triggers/auto-process")
def auto_process(db: Session = Depends(get_db)):
    """Auto-trigger claims for all active policies based on current weather."""
    return auto_trigger_claims(db)

# ── Health check ──────────────────────────────────────────────

@app.get("/")
def root():
    return {
        "app":     "GigShield API",
        "status":  "running",
        "version": "1.0.0",
        "docs":    "/docs"
    }