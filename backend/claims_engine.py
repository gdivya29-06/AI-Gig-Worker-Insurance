
import uuid
from datetime import datetime
from sqlalchemy.orm import Session
from database import Claim, Policy, Payout, Worker, DisruptionLog
from fraud_detection import run_fraud_detection
from weather import detect_disruptions

def _get_active_policy(worker_id: int, db: Session):
    now = datetime.utcnow()
    return db.query(Policy).filter(
        Policy.worker_id == worker_id,
        Policy.status == "active",
        Policy.end_date >= now
    ).first()

def _calculate_claim_amount(policy: Policy, disruption_severity: str) -> float:
    """
    Calculate payout based on coverage and disruption severity.
    high   → 100% of daily coverage
    medium → 60% of daily coverage
    low    → 30% of daily coverage
    """
    daily_coverage = policy.coverage_amount / 7   # weekly → daily
    multipliers = {"high": 1.0, "medium": 0.6, "low": 0.3}
    mult = multipliers.get(disruption_severity, 0.6)
    return round(daily_coverage * mult, 2)

def _process_mock_payout(worker: Worker, claim: Claim, db: Session) -> Payout:
    """Simulate UPI payout — in production replace with Razorpay/UPI API."""
    payout = Payout(
        claim_id       = claim.id,
        worker_id      = worker.id,
        amount         = claim.approved_amount,
        method         = "UPI",
        status         = "processed",
        transaction_id = f"TXN{uuid.uuid4().hex[:12].upper()}",
        processed_at   = datetime.utcnow(),
    )
    db.add(payout)
    db.commit()
    db.refresh(payout)
    return payout

def initiate_claim(worker_id: int, trigger_type: str, db: Session) -> dict:
    """
    Main entry point for claim processing.
    Called manually by worker OR automatically by trigger engine.
    """
    # 1 — Get worker
    worker = db.query(Worker).filter(Worker.id == worker_id).first()
    if not worker:
        return {"success": False, "message": "Worker not found"}

    # 2 — Get active policy
    policy = _get_active_policy(worker_id, db)
    if not policy:
        return {"success": False, "message": "No active policy. Please purchase a weekly plan first."}

    # 3 — Run fraud detection
    fraud_result = run_fraud_detection(
        worker_id    = worker_id,
        policy_id    = policy.id,
        trigger_type = trigger_type,
        city         = worker.city,
        db           = db
    )

    # 4 — Get disruption details for claim amount
    disruption_data = detect_disruptions(worker.city)
    severity = "medium"
    trigger_value = f"Auto-detected: {trigger_type}"

    for d in disruption_data.get("disruptions", []):
        if d["type"] == trigger_type:
            severity      = d["severity"]
            trigger_value = d["value"]
            break

    # 5 — Calculate claim amount
    claimed_amount = _calculate_claim_amount(policy, severity)

    # 6 — Determine approval
    if fraud_result["decision"] == "rejected":
        claim = Claim(
            worker_id      = worker_id,
            policy_id      = policy.id,
            trigger_type   = trigger_type,
            trigger_value  = trigger_value,
            claimed_amount = claimed_amount,
            approved_amount= 0,
            status         = "rejected",
            fraud_score    = fraud_result["fraud_score"],
            fraud_reason   = "; ".join(fraud_result["reasons"]),
            resolved_at    = datetime.utcnow(),
        )
        db.add(claim)
        db.commit()
        db.refresh(claim)
        return {
            "success":     False,
            "claim_id":    claim.id,
            "status":      "rejected",
            "message":     "Claim rejected due to fraud detection",
            "reasons":     fraud_result["reasons"],
            "fraud_score": fraud_result["fraud_score"],
        }

    elif fraud_result["decision"] == "manual_review":
        claim = Claim(
            worker_id      = worker_id,
            policy_id      = policy.id,
            trigger_type   = trigger_type,
            trigger_value  = trigger_value,
            claimed_amount = claimed_amount,
            approved_amount= 0,
            status         = "under_review",
            fraud_score    = fraud_result["fraud_score"],
            fraud_reason   = "; ".join(fraud_result["reasons"]),
        )
        db.add(claim)
        db.commit()
        db.refresh(claim)
        return {
            "success":  True,
            "claim_id": claim.id,
            "status":   "under_review",
            "message":  "Claim flagged for manual review. Will be processed within 24 hours.",
            "fraud_score": fraud_result["fraud_score"],
        }

    else:
        # Auto-approved
        claim = Claim(
            worker_id      = worker_id,
            policy_id      = policy.id,
            trigger_type   = trigger_type,
            trigger_value  = trigger_value,
            claimed_amount = claimed_amount,
            approved_amount= claimed_amount,
            status         = "approved",
            fraud_score    = fraud_result["fraud_score"],
            fraud_reason   = "",
            resolved_at    = datetime.utcnow(),
        )
        db.add(claim)
        db.commit()
        db.refresh(claim)

        # 7 — Process payout immediately
        payout = _process_mock_payout(worker, claim, db)

        # 8 — Log disruption
        log = DisruptionLog(
            city             = worker.city,
            disruption_type  = trigger_type,
            severity         = severity,
            raw_value        = trigger_value,
        )
        db.add(log)
        db.commit()

        return {
            "success":        True,
            "claim_id":       claim.id,
            "status":         "approved",
            "message":        f"✅ Claim approved! ₹{claimed_amount} will be credited to your UPI.",
            "approved_amount": claimed_amount,
            "payout": {
                "transaction_id": payout.transaction_id,
                "amount":         payout.amount,
                "method":         payout.method,
                "status":         payout.status,
            }
        }

def auto_trigger_claims(db: Session) -> dict:
    """
    Called periodically (or via endpoint) to auto-check weather
    and trigger claims for ALL workers with active policies.
    """
    now = datetime.utcnow()
    active_policies = db.query(Policy).filter(
        Policy.status == "active",
        Policy.end_date >= now
    ).all()

    triggered = []
    for policy in active_policies:
        disruption_data = detect_disruptions(policy.city)
        if disruption_data["is_disrupted"]:
            for disruption in disruption_data["disruptions"]:
                if disruption["severity"] in ["high", "medium"]:
                    result = initiate_claim(
                        worker_id    = policy.worker_id,
                        trigger_type = disruption["type"],
                        db           = db
                    )
                    triggered.append({
                        "worker_id": policy.worker_id,
                        "city":      policy.city,
                        "trigger":   disruption["type"],
                        "result":    result,
                    })

    return {
        "policies_checked": len(active_policies),
        "claims_triggered": len(triggered),
        "details":          triggered,
    }
