
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from database import Claim, Policy

# ── Fraud score thresholds ────────────────────────────────────
# Score 0–1; above 0.7 = rejected, 0.4–0.7 = manual review
FRAUD_REJECT_THRESHOLD = 0.70
FRAUD_REVIEW_THRESHOLD = 0.40

def check_duplicate_claim(worker_id: int, db: Session) -> tuple[float, str]:
    """Check if worker already filed a claim today."""
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0)
    existing = db.query(Claim).filter(
        Claim.worker_id == worker_id,
        Claim.created_at >= today_start
    ).first()
    if existing:
        return 0.9, "Duplicate claim: already filed a claim today"
    return 0.0, ""

def check_active_policy(worker_id: int, db: Session) -> tuple[float, str]:
    """Check if worker has an active policy."""
    now = datetime.utcnow()
    policy = db.query(Policy).filter(
        Policy.worker_id == worker_id,
        Policy.status == "active",
        Policy.end_date >= now
    ).first()
    if not policy:
        return 1.0, "No active policy found for this worker"
    return 0.0, ""

def check_claim_frequency(worker_id: int, db: Session) -> tuple[float, str]:
    """Flag if worker has filed more than 3 claims in the last 30 days."""
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    recent_claims = db.query(Claim).filter(
        Claim.worker_id == worker_id,
        Claim.created_at >= thirty_days_ago
    ).count()
    if recent_claims >= 5:
        return 0.8, f"High frequency: {recent_claims} claims in last 30 days"
    if recent_claims >= 3:
        return 0.4, f"Moderate frequency: {recent_claims} claims in last 30 days"
    return 0.0, ""

def check_weather_match(trigger_type: str, city: str) -> tuple[float, str]:
    """
    Verify the claimed disruption type matches actual weather conditions.
    Imports weather module to get current conditions.
    """
    try:
        from weather import detect_disruptions
        result = detect_disruptions(city)

        # Get all active disruption types
        active_types = [d["type"] for d in result.get("disruptions", [])]

        if not result["is_disrupted"]:
            return 0.85, f"No disruption detected in {city} currently"

        if trigger_type not in active_types:
            return 0.6, f"Claimed '{trigger_type}' but active disruptions are: {active_types}"

        return 0.0, ""
    except Exception:
        return 0.0, ""  # If check fails, don't penalize

def run_fraud_detection(
    worker_id: int,
    policy_id: int,
    trigger_type: str,
    city: str,
    db: Session
) -> dict:
    """
    Run all fraud checks and return combined score + decision.
    """
    checks = []
    total_score = 0.0
    reasons = []

    # Run each check
    checks_to_run = [
        ("duplicate_claim",  check_duplicate_claim(worker_id, db)),
        ("active_policy",    check_active_policy(worker_id, db)),
        ("claim_frequency",  check_claim_frequency(worker_id, db)),
        ("weather_match",    check_weather_match(trigger_type, city)),
    ]

    for check_name, (score, reason) in checks_to_run:
        checks.append({"check": check_name, "score": score, "reason": reason})
        if score > 0:
            total_score = max(total_score, score)   # take worst score
            if reason:
                reasons.append(reason)

    total_score = round(total_score, 3)

    if total_score >= FRAUD_REJECT_THRESHOLD:
        decision = "rejected"
    elif total_score >= FRAUD_REVIEW_THRESHOLD:
        decision = "manual_review"
    else:
        decision = "approved"

    return {
        "fraud_score":  total_score,
        "decision":     decision,
        "reasons":      reasons,
        "checks":       checks,
    }