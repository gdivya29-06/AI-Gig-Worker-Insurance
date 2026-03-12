from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from database import get_db, Worker, Policy, Claim, Payout
from datetime import datetime, timedelta

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("/worker/{worker_id}")
def worker_dashboard(worker_id: int, db: Session = Depends(get_db)):
    worker = db.query(Worker).filter(Worker.id == worker_id).first()
    if not worker:
        return {"error": "Worker not found"}

    now = datetime.utcnow()

    # Active policy
    active_policy = db.query(Policy).filter(
        Policy.worker_id == worker_id,
        Policy.status == "active",
        Policy.end_date >= now
    ).first()

    # Claim stats
    total_claims    = db.query(Claim).filter(Claim.worker_id == worker_id).count()
    approved_claims = db.query(Claim).filter(Claim.worker_id == worker_id, Claim.status == "approved").count()
    rejected_claims = db.query(Claim).filter(Claim.worker_id == worker_id, Claim.status == "rejected").count()

    # Total payout received
    payouts = db.query(Payout).filter(Payout.worker_id == worker_id).all()
    total_payout = sum(p.amount for p in payouts)

    # Recent claims (last 5)
    recent_claims = db.query(Claim).filter(
        Claim.worker_id == worker_id
    ).order_by(Claim.created_at.desc()).limit(5).all()

    return {
        "worker": {
            "name":     worker.name,
            "city":     worker.city,
            "zone":     worker.zone,
            "platform": worker.platform,
            "avg_daily_income": worker.avg_daily_income,
        },
        "active_policy": {
            "policy_id":        active_policy.id          if active_policy else None,
            "weekly_premium":   active_policy.weekly_premium  if active_policy else None,
            "coverage_amount":  active_policy.coverage_amount if active_policy else None,
            "expires":          active_policy.end_date.isoformat() if active_policy else None,
            "days_remaining":   (active_policy.end_date - now).days if active_policy else 0,
        } if active_policy else None,
        "claim_summary": {
            "total":    total_claims,
            "approved": approved_claims,
            "rejected": rejected_claims,
            "approval_rate": round(approved_claims / total_claims * 100, 1) if total_claims > 0 else 0,
        },
        "total_income_protected": round(total_payout, 2),
        "recent_claims": [
            {
                "claim_id":     c.id,
                "trigger":      c.trigger_type,
                "amount":       c.approved_amount,
                "status":       c.status,
                "date":         c.created_at.isoformat(),
            }
            for c in recent_claims
        ]
    }

@router.get("/admin")
def admin_dashboard(db: Session = Depends(get_db)):
    now = datetime.utcnow()
    thirty_days_ago = now - timedelta(days=30)

    total_workers  = db.query(Worker).count()
    active_policies = db.query(Policy).filter(
        Policy.status == "active", Policy.end_date >= now
    ).count()
    total_policies  = db.query(Policy).count()

    total_claims    = db.query(Claim).count()
    approved_claims = db.query(Claim).filter(Claim.status == "approved").count()
    rejected_claims = db.query(Claim).filter(Claim.status == "rejected").count()

    # Premium collected (last 30 days)
    recent_policies = db.query(Policy).filter(Policy.start_date >= thirty_days_ago).all()
    premium_collected = sum(p.weekly_premium for p in recent_policies)

    # Payouts made (last 30 days)
    recent_payouts = db.query(Payout).filter(Payout.processed_at >= thirty_days_ago).all()
    total_payouts = sum(p.amount for p in recent_payouts)

    # Loss ratio = payouts / premiums
    loss_ratio = round(total_payouts / premium_collected * 100, 1) if premium_collected > 0 else 0

    # Claims by trigger type
    trigger_stats = db.query(
        Claim.trigger_type, func.count(Claim.id)
    ).group_by(Claim.trigger_type).all()

    # City-wise policy distribution
    city_stats = db.query(
        Policy.city, func.count(Policy.id)
    ).group_by(Policy.city).all()

    return {
        "overview": {
            "total_workers":    total_workers,
            "active_policies":  active_policies,
            "total_policies":   total_policies,
            "total_claims":     total_claims,
        },
        "financials_30d": {
            "premium_collected": round(premium_collected, 2),
            "total_payouts":     round(total_payouts, 2),
            "loss_ratio_pct":    loss_ratio,
            "net_balance":       round(premium_collected - total_payouts, 2),
        },
        "claims_analysis": {
            "approved": approved_claims,
            "rejected": rejected_claims,
            "approval_rate_pct": round(approved_claims / total_claims * 100, 1) if total_claims > 0 else 0,
            "by_trigger_type": {t: c for t, c in trigger_stats},
        },
        "geography": {
            "policies_by_city": {city: count for city, count in city_stats},
        }
    }