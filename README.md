# 🛵 GigShield — AI-Powered Parametric Income Insurance for Food Delivery Partners

> **Guidewire DEVTrails 2026** | Team: AI-Gig-Worker-Insurance  
> Persona: **Food Delivery Partners (Zomato / Swiggy)**  
> Coverage: **Income Loss ONLY** (No health, accident, or vehicle repair coverage)  
> Pricing Model: **Weekly Premium**

---

## 🧩 The Problem

India's food delivery partners (Zomato, Swiggy) earn ₹500–₹1,200/day entirely through active deliveries. External disruptions — heavy rain, extreme heat, air quality emergencies, flash floods, local curfews, bandhs — can wipe out an entire day or week of income with zero warning and zero protection.

**No work = No pay. No safety net exists today.**

GigShield changes that. When the rain stops orders, the payout starts automatically.

---

## 👤 Persona: The Food Delivery Partner

| Attribute | Details |
|---|---|
| Name | Ravi (representative persona) |
| Platform | Zomato / Swiggy active partner |
| Daily earnings | ₹600–₹1,200 (order-dependent) |
| Peak hours | 12–2 PM, 7–10 PM |
| Biggest fear | Monsoon weeks, heatwave afternoons, sudden curfews |
| Tech comfort | Smartphone-first, prefers simple UI |
| Payment cycle | Weekly settlements from platform |

### Scenario Walkthroughs

**Scenario 1 — Monsoon Shutdown (Environmental)**  
> Mumbai, July. IMD issues a Red Alert. Rainfall exceeds 115mm in 3 hours. Zomato suspends deliveries in 4 zones. Ravi loses ₹900 in a day. GigShield detects the Red Alert via weather API, auto-triggers a claim, and credits ₹720 (80% coverage) to Ravi's UPI within the hour. Zero action needed from Ravi.

**Scenario 2 — AQI Emergency (Environmental)**  
> Delhi, November. AQI crosses 400 (Severe). GRAP Stage IV restrictions announced. Outdoor activity discouraged. Ravi can't safely operate. GigShield triggers income protection for the day automatically.

**Scenario 3 — Local Bandh / Curfew (Social)**  
> Hyderabad. Unplanned city-wide bandh called. No pickups accessible. GigShield cross-references a news/social trigger API, flags the disruption, and initiates coverage for affected zone workers.

---

## ⚙️ Application Workflow

```
Worker Onboarding
      ↓
Risk Profile Creation (AI scoring)
      ↓
Weekly Policy Purchase (Dynamic Premium)
      ↓
Real-Time Disruption Monitoring (APIs)
      ↓
Auto Trigger Detected? → YES → Claim Auto-Initiated
      ↓                    NO  → Continue Monitoring
Fraud Detection Layer
      ↓
Claim Approved → Instant UPI Payout
      ↓
Dashboard Updated (Worker + Admin)
```

---

## 💰 Weekly Premium Model

GigShield operates on a **weekly premium** aligned with the Zomato/Swiggy weekly payout cycle. Workers subscribe week-to-week — no long-term commitments.

### Base Premium Tiers (Weekly)

| Plan | Weekly Premium | Max Weekly Payout | Coverage Days |
|---|---|---|---|
| Basic Shield | ₹29 | ₹700 | Up to 2 disruption days |
| Standard Shield | ₹49 | ₹1,400 | Up to 4 disruption days |
| Full Shield | ₹79 | ₹2,500 | Unlimited disruption days |

### Dynamic Premium Calculation (AI-Adjusted)

Base premium is **dynamically adjusted** each week using the following factors:

```
Weekly Premium = Base Rate
  × Weather Risk Factor (0.8 – 1.5)  ← Based on 7-day forecast for worker's city
  × Zone Risk Score (0.9 – 1.3)      ← Historical flood/disruption rate for delivery zone
  × Claim History Factor (0.95 – 1.2) ← Penalizes frequent claimers slightly
  × Season Multiplier (0.9 – 1.4)    ← Monsoon/winter spikes
```

**Example:** Ravi in Mumbai in July (monsoon peak) on Standard Shield:  
`₹49 × 1.4 (weather) × 1.2 (zone) × 1.0 (clean history) × 1.3 (season) = ~₹107/week`  
Payout potential: ₹1,400. ROI for worker if 2 rain days hit: 13x.

---

## ⚡ Parametric Triggers (Automated — No Claim Filing Needed)

| Trigger | Data Source | Threshold | Action |
|---|---|---|---|
| Heavy Rainfall | OpenWeatherMap API | > 64.5mm/hr (IMD Red Alert) | Auto-claim initiated |
| Extreme Heat | OpenWeatherMap API | > 45°C (Heat Wave) | Auto-claim initiated |
| Severe Air Quality | AQICN / OpenAQ API | AQI > 300 (Very Poor) | Auto-claim initiated |
| Flash Flood Warning | IMD mock / alert feed | Flood warning issued for city | Auto-claim initiated |
| Local Curfew / Bandh | News API / mock feed | Verified curfew in worker zone | Auto-claim initiated |

**Key:** Triggers are **objective and verifiable** — no subjective proof required from the worker.

---

## 🤖 AI/ML Integration Plan

### 1. Risk Scoring Engine (Phase 1 → Phase 2)
- Input features: city, delivery zone, historical disruption frequency, platform (Zomato/Swiggy), months active, average weekly orders
- Model: Rule-based scoring (Phase 1) → Gradient Boosted model trained on synthetic disruption + earnings data (Phase 2)
- Output: Risk Score (0–100) used to set premium multiplier

### 2. Dynamic Premium Calculator
- Runs every Sunday night (before new week starts)
- Pulls 7-day weather forecast, historical zone data, and worker profile
- Outputs personalized weekly premium for each active worker

### 3. Fraud Detection (Phase 2 → Phase 3)
- **GPS Spoofing Detection:** Cross-check worker's last known location with claimed disruption zone
- **Claim Pattern Anomaly:** Flag if a worker claims every single disruption trigger (statistical outlier detection)
- **Duplicate Prevention:** Hash-based deduplication of claims by worker ID + trigger event ID
- **Historical Validation:** If worker logged 0 orders in the past 30 days before signing up → flag as suspicious

---

## 🛠️ Tech Stack

### Backend
| Component | Technology |
|---|---|
| API Framework | FastAPI (Python) |
| Database | SQLite (dev) / PostgreSQL (prod) |
| ML/Scoring | Scikit-learn + Pandas |
| Weather Data | OpenWeatherMap API (free tier) |
| AQI Data | AQICN API (free tier) |
| Task Scheduling | APScheduler (trigger monitoring loop) |

### Frontend
| Component | Technology |
|---|---|
| UI Framework | React + Tailwind CSS |
| Charts / Dashboard | Recharts |
| HTTP Client | Axios |

### Infrastructure
| Component | Technology |
|---|---|
| Deployment | Local / Render (free tier) |
| Auth | JWT (simple token auth) |
| Payment (mock) | Razorpay test mode / UPI simulator |

---

## 🗂️ Repository Structure

```
AI-Gig-Worker-Insurance/
├── backend/
│   ├── main.py              # FastAPI app entry point
│   ├── models/              # DB models (Worker, Policy, Claim)
│   ├── routers/             # API routes (onboarding, claims, triggers)
│   ├── services/
│   │   ├── risk_engine.py   # AI risk scoring + premium calculation
│   │   ├── trigger_monitor.py # Real-time disruption detection
│   │   └── fraud_detector.py  # Fraud detection logic
│   └── utils/               # Weather API, AQI API helpers
├── frontend/
│   ├── src/
│   │   ├── pages/           # Onboarding, Dashboard, Claims, Policy
│   │   └── components/      # Reusable UI components
├── data/
│   └── sample_data.csv      # Synthetic worker + disruption data
├── tests/
│   └── test_cases.py        # Unit tests
├── docs/
│   └── architecture.png     # System architecture diagram
├── demo/
│   └── demo_video_link.txt  # Link to 2-min demo video
├── requirements.txt
└── README.md
```

---

## 📅 Development Plan

### Phase 1 (Mar 4–20) — Ideation & Foundation ✅
- [x] Persona research & use-case definition
- [x] Weekly premium model design
- [x] Parametric trigger definition
- [x] Tech stack selection & repo setup
- [x] Backend scaffold (FastAPI)
- [x] Frontend scaffold (React)
- [ ] README finalized ← *this document*
- [ ] 2-minute strategy video

### Phase 2 (Mar 21–Apr 4) — Core Build
- [ ] Worker registration + onboarding flow
- [ ] Policy creation with dynamic premium calculation
- [ ] Weather/AQI API integration (3–5 triggers live)
- [ ] Claims management (auto-trigger → auto-approve pipeline)
- [ ] Basic fraud detection (GPS + duplicate check)
- [ ] Worker dashboard (React)

### Phase 3 (Apr 5–17) — Scale & Polish
- [ ] Advanced fraud detection (anomaly scoring)
- [ ] Mock UPI payout integration (Razorpay test mode)
- [ ] Admin/Insurer dashboard (loss ratios, predictive analytics)
- [ ] Final pitch deck (PDF)
- [ ] 5-minute walkthrough demo video

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                      FRONTEND (React)                    │
│  Onboarding | Policy | Claims | Worker Dashboard | Admin │
└────────────────────────┬────────────────────────────────┘
                         │ REST API (Axios)
┌────────────────────────▼────────────────────────────────┐
│                   BACKEND (FastAPI)                      │
│  ┌─────────────┐  ┌──────────────┐  ┌────────────────┐  │
│  │ Risk Engine │  │ Trigger Mon. │  │ Fraud Detector │  │
│  │ (AI/ML)     │  │ (Scheduler)  │  │ (Rules + ML)   │  │
│  └─────────────┘  └──────┬───────┘  └────────────────┘  │
└─────────────────────────┼───────────────────────────────┘
                          │
         ┌────────────────┼────────────────┐
         ▼                ▼                ▼
  OpenWeatherMap       AQICN API      News/Mock API
  (Rain, Heat)        (AQI levels)    (Curfew/Bandh)
         │
┌────────▼──────────┐
│  SQLite / Postgres │
│  Workers, Policies │
│  Claims, Triggers  │
└────────────────────┘
```

---

## 👥 Team

| Member | Role | Responsibilities |
|---|---|---|
| Zahra | AI + Backend Engineer | Risk model, premium calculation, triggers, fraud detection, APIs |
| Divya | Frontend + UX | Worker onboarding UI, policy screens, dashboards |
| Vyom | Strategy + Docs | Persona research, pricing model, architecture, README, demo |

---

## 🔗 Links

- **Demo Video (Phase 1):** [To be added before March 20 EOD]
- **Live App (Phase 2+):** Coming soon

---

*Built for Guidewire DEVTrails 2026 — "Seed. Scale. Soar."*
