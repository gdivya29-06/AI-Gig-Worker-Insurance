from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime, timedelta

from database import init_db, get_db, Policy, Claim, Worker
from auth import router as auth_router
from dashboard import router as dashboard_router
from ml_premium_model import ml_calculate_premium
from claims_engine import initiate_claim, auto_trigger_claims
from triggers import detect_all_disruptions, detect_disruptions

# ── App setup ─────────────────────────────────────────────────
app = FastAPI(
    title="GigShield — AI Insurance for Food Delivery Workers",
    description="Parametric income insurance for Zomato/Swiggy delivery partners",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Init DB + ML Model on startup ─────────────────────────────
@app.on_event("startup")
def startup():
    init_db()
    print("✅ Database initialized")
    # Pre-load ML model
    try:
        from ml_premium_model import get_model
        get_model()
        print("✅ ML Premium Model loaded")
    except Exception as e:
        print(f"⚠️ ML model load failed: {e}")

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
    """ML-powered dynamic premium calculation."""
    return ml_calculate_premium(
        city             = req.city,
        zone             = req.zone,
        experience_years = req.experience_years,
        avg_daily_income = req.avg_daily_income,
        platform         = req.platform,
        tier             = req.tier,
    )

# ── Policy endpoints ──────────────────────────────────────────
class PolicyRequest(BaseModel):
    worker_id: int
    tier: str = "standard"

@app.post("/policy/create")
def create_policy(req: PolicyRequest, db: Session = Depends(get_db)):
    worker = db.query(Worker).filter(Worker.id == req.worker_id).first()
    if not worker:
        raise HTTPException(status_code=404, detail="Worker not found")

    now = datetime.utcnow()
    existing = db.query(Policy).filter(
        Policy.worker_id == req.worker_id,
        Policy.status    == "active",
        Policy.end_date  >= now
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Worker already has an active policy")

    # Use ML model for premium
    premium_data = ml_calculate_premium(
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
        "message":         "✅ Policy created successfully!",
        "policy_id":       policy.id,
        "weekly_premium":  policy.weekly_premium,
        "coverage_amount": policy.coverage_amount,
        "valid_until":     policy.end_date.isoformat(),
        "risk_level":      premium_data["risk_level"],
        "tier":            premium_data["tier"],
        "model_used":      premium_data.get("model_used", "ML"),
    }

@app.get("/policy/active/{worker_id}")
def get_active_policy(worker_id: int, db: Session = Depends(get_db)):
    now = datetime.utcnow()
    policy = db.query(Policy).filter(
        Policy.worker_id == worker_id,
        Policy.status    == "active",
        Policy.end_date  >= now
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
    worker_id:    int
    trigger_type: str

@app.post("/claims/initiate")
def file_claim(req: ClaimRequest, db: Session = Depends(get_db)):
    return initiate_claim(req.worker_id, req.trigger_type, db)

@app.get("/claims/status/{claim_id}")
def claim_status(claim_id: int, db: Session = Depends(get_db)):
    claim = db.query(Claim).filter(Claim.id == claim_id).first()
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")
    return {
        "claim_id":        claim.id,
        "worker_id":       claim.worker_id,
        "trigger_type":    claim.trigger_type,
        "trigger_value":   claim.trigger_value,
        "claimed_amount":  claim.claimed_amount,
        "approved_amount": claim.approved_amount,
        "status":          claim.status,
        "fraud_score":     claim.fraud_score,
        "created_at":      claim.created_at.isoformat(),
        "resolved_at":     claim.resolved_at.isoformat() if claim.resolved_at else None,
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
                "claim_id":        c.id,
                "trigger_type":    c.trigger_type,
                "claimed_amount":  c.claimed_amount,
                "approved_amount": c.approved_amount,
                "status":          c.status,
                "date":            c.created_at.isoformat(),
            }
            for c in claims
        ]
    }

# ── Trigger endpoints — 5 automated triggers ─────────────────
@app.get("/triggers/check/{city}")
def check_triggers(city: str, platform: str = "zomato"):
    """Check all 5 disruption triggers for a city."""
    return detect_all_disruptions(city, platform)

@app.get("/triggers/check/{city}/{platform}")
def check_triggers_with_platform(city: str, platform: str):
    """Check all 5 disruption triggers for city + platform."""
    return detect_all_disruptions(city, platform)

@app.post("/triggers/auto-process")
def auto_process(db: Session = Depends(get_db)):
    """Auto-trigger claims for all active policies."""
    return auto_trigger_claims(db)

@app.get("/triggers/summary")
def triggers_summary():
    """Get summary of all 5 trigger types."""
    return {
        "triggers": [
            {
                "id": 1,
                "name": "Heavy Rain / Flood",
                "type": "heavy_rain / flood_risk",
                "threshold": "Rainfall > 20mm/hr (medium) or > 50mm/hr (high)",
                "data_source": "OpenWeatherMap API",
                "income_loss": "60-100%"
            },
            {
                "id": 2,
                "name": "Extreme Heat",
                "type": "extreme_heat",
                "threshold": "Temperature > 42°C (medium) or > 45°C (high)",
                "data_source": "OpenWeatherMap API",
                "income_loss": "40-80%"
            },
            {
                "id": 3,
                "name": "Severe Air Pollution",
                "type": "poor_aqi / severe_pollution",
                "threshold": "AQI Index 4 (Poor) or 5 (Severe)",
                "data_source": "OpenWeatherMap Air Pollution API",
                "income_loss": "30-70%"
            },
            {
                "id": 4,
                "name": "Curfew / Civil Unrest",
                "type": "curfew",
                "threshold": "Active government-imposed curfew",
                "data_source": "Government alerts API (mock)",
                "income_loss": "100%"
            },
            {
                "id": 5,
                "name": "Platform App Outage",
                "type": "platform_outage",
                "threshold": "Delivery app down or severely degraded",
                "data_source": "Platform status API (mock)",
                "income_loss": "50-100%"
            },
        ]
    }

# ── Health check ──────────────────────────────────────────────
@app.get("/")
def root():
    return {
        "app":      "GigShield API",
        "status":   "running",
        "version":  "2.0.0",
        "features": [
            "ML-powered premium calculation",
            "5 automated disruption triggers",
            "Zero-touch claim processing",
            "AI fraud detection",
            "Instant mock UPI payouts"
        ],
        "docs": "/docs"
    }