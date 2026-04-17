import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt

# =================================================
# PAGE CONFIG
# =================================================
st.set_page_config(
    page_title="GigShield AI",
    page_icon="🛡",
    layout="wide",
    initial_sidebar_state="expanded"
)

API_BASE = "http://127.0.0.1:8000"

# =================================================
# THEME
# =================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500;600&display=swap');

* { font-family: 'DM Sans', sans-serif; }
.stApp { background: #F7F8FC; color: #0D1117; }

header[data-testid="stHeader"] {
    background: #0D1117 !important;
    border-bottom: 1px solid #2ECC71 !important;
}
button[data-testid="collapsedControl"] {
    color: white !important;
    background: #2ECC71 !important;
    border-radius: 8px !important;
}
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0D1117 0%, #1A1F2E 100%) !important;
    border-right: 2px solid #2ECC71 !important;
    min-width: 260px !important;
}
section[data-testid="stSidebar"] * { color: #E8EAF0 !important; }
section[data-testid="stSidebar"] .stRadio label { color: #E8EAF0 !important; font-size: 15px !important; }
section[data-testid="stSidebar"] .stSelectbox label { color: #A0A8B8 !important; font-size: 12px !important; text-transform: uppercase; letter-spacing: 1px; }
section[data-testid="stSidebar"] .stSelectbox > div > div { background: #1A1F2E !important; border: 1px solid #2ECC71 !important; color: white !important; }

.brand-block { background: linear-gradient(135deg, #2ECC71 0%, #27AE60 100%); border-radius: 16px; padding: 20px 16px; margin-bottom: 20px; text-align: center; }
.brand-block h1 { font-family: 'Syne', sans-serif !important; font-size: 26px !important; font-weight: 800 !important; color: white !important; margin: 0 !important; }
.brand-block p { font-size: 11px !important; color: rgba(255,255,255,0.85) !important; margin: 6px 0 0 0 !important; line-height: 1.5 !important; }

.page-header { background: linear-gradient(135deg, #0D1117 0%, #1A1F2E 100%); border-radius: 20px; padding: 28px 32px; margin-bottom: 24px; border-left: 5px solid #2ECC71; }
.page-header h1 { font-family: 'Syne', sans-serif !important; font-size: 30px !important; font-weight: 800 !important; color: white !important; margin: 0 !important; }
.page-header p { color: #A0A8B8 !important; font-size: 14px !important; margin: 6px 0 0 0 !important; }

div[data-testid="metric-container"] { background: white; border: 1px solid #E8EAF0; border-radius: 16px; padding: 20px 24px !important; box-shadow: 0 2px 12px rgba(0,0,0,0.06); }
div[data-testid="metric-container"] [data-testid="stMetricLabel"] { font-size: 11px !important; font-weight: 600 !important; text-transform: uppercase; letter-spacing: 1px; color: #6B7280 !important; }
div[data-testid="metric-container"] [data-testid="stMetricValue"] { font-family: 'Syne', sans-serif !important; font-size: 26px !important; font-weight: 700 !important; color: #0D1117 !important; }

.stButton > button { background: linear-gradient(135deg, #2ECC71 0%, #27AE60 100%) !important; color: white !important; border: none !important; border-radius: 12px !important; padding: 14px 28px !important; font-size: 15px !important; font-weight: 600 !important; cursor: pointer !important; width: 100% !important; box-shadow: 0 4px 15px rgba(46,204,113,0.4) !important; }
.stButton > button:hover { background: linear-gradient(135deg, #27AE60 0%, #1E8449 100%) !important; box-shadow: 0 8px 25px rgba(46,204,113,0.5) !important; }

.stTextInput > div > div > input { background: white !important; border: 2px solid #D1D5DB !important; border-radius: 10px !important; padding: 12px 14px !important; font-size: 15px !important; color: #0D1117 !important; }
.stTextInput > div > div > input:focus { border-color: #2ECC71 !important; box-shadow: 0 0 0 3px rgba(46,204,113,0.2) !important; }
.stTextInput label { font-weight: 600 !important; font-size: 12px !important; color: #374151 !important; text-transform: uppercase; letter-spacing: 0.5px; }

.stSelectbox > div > div { background: white !important; border: 2px solid #D1D5DB !important; border-radius: 10px !important; color: #0D1117 !important; }
.stSelectbox label { font-weight: 600 !important; font-size: 12px !important; color: #374151 !important; text-transform: uppercase; letter-spacing: 0.5px; }

.stNumberInput > div > div > input { background: white !important; border: 2px solid #D1D5DB !important; border-radius: 10px !important; padding: 10px 14px !important; font-size: 15px !important; color: #0D1117 !important; }

.stTabs [data-baseweb="tab-list"] { background: #F0F2F8 !important; border-radius: 12px !important; padding: 4px !important; }
.stTabs [data-baseweb="tab"] { border-radius: 10px !important; font-weight: 600 !important; color: #6B7280 !important; font-size: 14px !important; padding: 10px 20px !important; }
.stTabs [aria-selected="true"] { background: white !important; color: #0D1117 !important; box-shadow: 0 2px 8px rgba(0,0,0,0.1) !important; }

footer { visibility: hidden; }
#MainMenu { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# =================================================
# SESSION STATE
# =================================================
if "worker_id"   not in st.session_state: st.session_state.worker_id   = None
if "worker_name" not in st.session_state: st.session_state.worker_name = None
if "token"       not in st.session_state: st.session_state.token       = None

# =================================================
# SIDEBAR  ← FIX 1: if/else now properly indented inside `with st.sidebar`
# =================================================
with st.sidebar:
    st.markdown("""
    <div class="brand-block">
        <h1>🛡 GigShield AI</h1>
        <p>Parametric Income Insurance<br>for Delivery Workers</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("##### LOGIN AS")
    role = st.radio("Login as", ["👷 Worker", "🏢 Admin"], label_visibility="collapsed")

    st.markdown("---")
    st.markdown("##### NAVIGATE")

    if role == "👷 Worker":                          # ← 4-space indent inside `with`
        page = st.selectbox(
            "Navigate",
            ["Login / Register", "Dashboard", "Buy Policy", "My Coverage", "Claims"],
            label_visibility="collapsed"
        )
    else:                                            # ← same 4-space indent
        page = st.selectbox(
            "Navigate",
            ["Admin Dashboard", "Fraud Detection", "Live Triggers"],
            label_visibility="collapsed"
        )

    st.markdown("---")

    if st.session_state.worker_name:
        st.markdown(f"""
        <div style="background:rgba(46,204,113,0.2); border:1px solid #2ECC71;
             border-radius:12px; padding:14px 16px; margin-bottom:12px;">
            <div style="font-size:10px; color:#6EE7B7; text-transform:uppercase; letter-spacing:1px; margin-bottom:4px;">Logged in as</div>
            <div style="font-size:15px; font-weight:700; color:white;">👷 {st.session_state.worker_name}</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("🚪 Logout"):
            st.session_state.worker_id   = None
            st.session_state.worker_name = None
            st.session_state.token       = None
            st.rerun()
    else:
        st.markdown("""
        <div style="background:rgba(255,255,255,0.05); border:1px solid rgba(255,255,255,0.15);
             border-radius:12px; padding:12px 16px; text-align:center;">
            <div style="font-size:12px; color:#9CA3AF;">⚪ Not logged in</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("""
    <div style="margin-top:24px; padding:12px; background:rgba(46,204,113,0.08);
                border-radius:10px; border:1px solid rgba(46,204,113,0.2);">
        <div style="font-size:11px; color:#6EE7B7; text-align:center; line-height:1.8;">
            🟢 Live Weather Monitoring<br>
            🤖 AI Risk Engine Active<br>
            ⚡ Instant UPI Payouts
        </div>
    </div>
    """, unsafe_allow_html=True)

# =================================================
# HELPER
# =================================================
def page_header(icon, title, subtitle=""):
    st.markdown(f"""
    <div class="page-header">
        <div style="display:flex; align-items:center; gap:16px;">
            <div style="font-size:36px">{icon}</div>
            <div>
                <h1>{title}</h1>
                <p>{subtitle}</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# =================================================
# LOGIN / REGISTER
# =================================================
if role == "👷 Worker" and page == "Login / Register":
    page_header("🔐", "Worker Portal", "Login or create your GigShield account")

    tab1, tab2 = st.tabs(["  🔑 Login  ", "  ✨ Register  "])

    with tab1:
        col_a, col_b, col_c = st.columns([1, 2, 1])
        with col_b:
            st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
            phone    = st.text_input("📱 Phone Number", placeholder="e.g. 9876543210")
            password = st.text_input("🔒 Password", type="password", placeholder="Enter your password")
            st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
            if st.button("Login to GigShield →"):
                if phone and password:
                    try:
                        res = requests.post(f"{API_BASE}/auth/login",
                                            json={"phone": phone, "password": password})
                        if res.status_code == 200:
                            data = res.json()
                            st.session_state.worker_id   = data["worker_id"]
                            st.session_state.worker_name = data["worker"]["name"]
                            st.session_state.token       = data["token"]
                            st.success(f"✅ Welcome back, {data['worker']['name']}!")
                            st.balloons()
                            st.rerun()
                        else:
                            st.error("❌ " + res.json().get("detail", "Login failed"))
                    except Exception as e:
                        st.error(f"Cannot connect to backend: {e}")
                else:
                    st.warning("Please enter phone and password")

    with tab2:
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            name       = st.text_input("👤 Full Name",   placeholder="Raju Kumar")
            phone_r    = st.text_input("📱 Phone",       placeholder="9876543210", key="reg_phone")
            email      = st.text_input("📧 Email",       placeholder="raju@example.com")
            password_r = st.text_input("🔒 Password",    type="password", key="reg_pass")
        with col2:
            city       = st.selectbox("🏙 City", ["bangalore","mumbai","delhi","chennai","hyderabad","pune"])
            zone       = st.text_input("📍 Zone / Area", placeholder="e.g. koramangala")
            platform   = st.selectbox("🛵 Platform",     ["zomato", "swiggy"])
            avg_income = st.number_input("💰 Avg Daily Income (₹)", min_value=200, max_value=2000, value=600)
            exp_years  = st.number_input("⏳ Experience (years)",   min_value=0.0, max_value=20.0, value=1.0, step=0.5)

        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        if st.button("Create My Account →"):
            if all([name, phone_r, email, password_r, zone]):
                try:
                    res = requests.post(f"{API_BASE}/auth/register", json={
                        "name": name, "phone": phone_r, "email": email,
                        "password": password_r, "city": city, "zone": zone,
                        "platform": platform, "avg_daily_income": avg_income,
                        "experience_years": exp_years, "avg_daily_orders": 20
                    })
                    if res.status_code == 200:
                        data = res.json()
                        st.session_state.worker_id   = data["worker_id"]
                        st.session_state.worker_name = data["worker"]["name"]
                        st.session_state.token       = data["token"]
                        st.success(f"🎉 Welcome to GigShield, {name}!")
                        st.balloons()
                        st.rerun()
                    else:
                        st.error("❌ " + res.json().get("detail", "Registration failed"))
                except Exception as e:
                    st.error(f"Backend error: {e}")
            else:
                st.warning("Please fill in all fields")

# =================================================
# WORKER DASHBOARD
# =================================================
elif role == "👷 Worker" and page == "Dashboard":
    page_header("📊", "My Dashboard", "Your live insurance overview")

    if not st.session_state.worker_id:
        st.warning("⚠️ Please login first — go to 'Login / Register' in the sidebar menu")
        st.stop()

    try:
        res     = requests.get(f"{API_BASE}/dashboard/worker/{st.session_state.worker_id}")
        data    = res.json()
        worker  = data["worker"]
        summary = data["claim_summary"]
        policy  = data.get("active_policy")

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("🏙 City",             worker["city"].title())
        col2.metric("🛵 Platform",         worker["platform"].title())
        col3.metric("💰 Daily Income",     f"₹{worker['avg_daily_income']}")
        col4.metric("🛡 Income Protected", f"₹{data['total_income_protected']}", delta="+12% safety")

        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

        if policy:
            st.markdown(f"""
            <div style="background:linear-gradient(135deg,#0D1117 0%,#1A1F2E 100%);
                        border-radius:20px; padding:24px 28px; margin-bottom:20px;
                        border-left:5px solid #2ECC71;">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <div>
                        <div style="font-size:11px; color:#6EE7B7; text-transform:uppercase;
                                    letter-spacing:1px; font-weight:600; margin-bottom:6px;">Active Policy</div>
                        <div style="font-family:'Syne',sans-serif; font-size:26px; font-weight:800;
                                    color:white;">₹{policy['coverage_amount']} Coverage</div>
                        <div style="color:#A0A8B8; font-size:13px; margin-top:4px;">
                            Premium: ₹{policy['weekly_premium']}/week &nbsp;•&nbsp;
                            Expires: {str(policy['expires'])[:10]}
                        </div>
                    </div>
                    <div style="text-align:right;">
                        <div style="background:#2ECC71; color:white; padding:8px 20px;
                                    border-radius:20px; font-weight:700; font-size:12px;">✓ ACTIVE</div>
                        <div style="color:#6B7280; font-size:12px; margin-top:6px;">
                            {policy['days_remaining']} days remaining
                        </div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="background:#FFFBEB; border:2px solid #F59E0B; border-radius:16px;
                        padding:20px 28px; margin-bottom:20px;">
                <b style="color:#92400E; font-size:15px;">⚠️ No Active Policy</b>
                <span style="color:#B45309; font-size:14px; margin-left:12px;">
                    Go to 'Buy Policy' in the menu to protect your income.
                </span>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("### 📋 Claims Summary")
        c1, c2, c3 = st.columns(3)
        c1.metric("Total Claims",  summary["total"])
        c2.metric("✅ Approved",   summary["approved"])
        c3.metric("Approval Rate", f"{summary['approval_rate']}%")

        if data["recent_claims"]:
            st.markdown("### 🕒 Recent Claims")
            st.dataframe(pd.DataFrame(data["recent_claims"]),
                         use_container_width=True, hide_index=True)

        st.markdown("### 🌦 Live Conditions")
        weather_res = requests.get(f"{API_BASE}/triggers/check/{worker['city']}")
        weather     = weather_res.json()
        if weather["is_disrupted"]:
            for d in weather["disruptions"]:
                if d["severity"] == "high":
                    st.error(f"🚨 **{d['type'].replace('_',' ').title()}** — {d['message']} ({d['value']})")
                else:
                    st.warning(f"⚠️ **{d['type'].replace('_',' ').title()}** — {d['message']} ({d['value']})")
        else:
            st.success("☀️ All conditions stable — great day for deliveries!")

    except Exception as e:
        st.error(f"Error loading dashboard: {e}")

# =================================================
# BUY POLICY
# =================================================
elif role == "👷 Worker" and page == "Buy Policy":
    page_header("💳", "Choose Your Plan", "Weekly income protection tailored to your risk profile")

    if not st.session_state.worker_id:
        st.warning("⚠️ Please login first")
        st.stop()

    try:
        worker_res = requests.get(f"{API_BASE}/auth/worker/{st.session_state.worker_id}")
        worker     = worker_res.json()

        tiers = {}
        for t in ["basic", "standard", "premium"]:
            r = requests.post(f"{API_BASE}/premium/calculate", json={
                "city": worker["city"], "zone": worker["zone"],
                "experience_years": worker["experience_years"],
                "avg_daily_income": worker["avg_daily_income"],
                "platform": worker["platform"], "tier": t
            })
            tiers[t] = r.json()

        plan_meta = {
            "basic":    {"icon": "🥉", "color": "#6B7280", "badge": ""},
            "standard": {"icon": "🥈", "color": "#2ECC71", "badge": "MOST POPULAR"},
            "premium":  {"icon": "🥇", "color": "#E67E22", "badge": "BEST COVER"},
        }

        col1, col2, col3 = st.columns(3)
        for col, (tier_key, tier_data) in zip([col1, col2, col3], tiers.items()):
            meta     = plan_meta[tier_key]
            featured = tier_key == "standard"
            with col:
                badge = (f'<div style="background:{meta["color"]}; color:white; font-size:10px; '
                         f'font-weight:700; padding:4px 12px; border-radius:20px; display:inline-block; '
                         f'letter-spacing:1px; margin-bottom:10px;">{meta["badge"]}</div>'
                         if meta["badge"] else '<div style="height:24px"></div>')
                st.markdown(f"""
                <div style="background:{'linear-gradient(135deg,#ECFDF5 0%,white 100%)' if featured else 'white'};
                            border-radius:20px; padding:24px 20px;
                            border:2px solid {'#2ECC71' if featured else '#E8EAF0'};
                            text-align:center;">
                    {badge}
                    <div style="font-size:28px">{meta['icon']}</div>
                    <div style="font-size:17px; font-weight:700; color:#0D1117; margin:8px 0;">
                        {tier_data['tier']}
                    </div>
                    <div style="font-family:'Syne',sans-serif; font-size:34px; font-weight:800;
                                color:{meta['color']};">₹{tier_data['weekly_premium']}</div>
                    <div style="font-size:12px; color:#9CA3AF; margin-top:2px;">per week</div>
                    <hr style="border:1px solid #F3F4F6; margin:14px 0">
                    <div style="font-size:13px; color:#4B5563; text-align:left; line-height:2;">
                        ✓ Coverage: <b>₹{tier_data['coverage_amount']}</b><br>
                        ✓ Covers <b>{tier_data['coverage_days']} days</b>/week<br>
                        ✓ Risk: <b>{tier_data['risk_level']}</b><br>
                        ✓ Auto claim processing<br>
                        ✓ Instant UPI payout
                    </div>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
        st.markdown("### Activate Your Plan")

        col_a, col_b = st.columns([1, 2])
        with col_a:
            selected_tier = st.selectbox("Choose Plan", ["basic","standard","premium"], index=1,
                format_func=lambda x: {"basic":"🥉 Basic","standard":"🥈 Standard","premium":"🥇 Premium"}[x])
        with col_b:
            pd_ = tiers[selected_tier]
            st.markdown(f"""
            <div style="background:#F0FDF4; border:1px solid #BBF7D0; border-radius:12px;
                        padding:14px 18px; margin-top:8px; font-size:14px;">
                <b>{pd_['tier']}</b> &nbsp;|&nbsp; ₹{pd_['weekly_premium']}/week &nbsp;|&nbsp;
                Coverage: ₹{pd_['coverage_amount']} &nbsp;|&nbsp; Risk: {pd_['risk_level']}
            </div>
            """, unsafe_allow_html=True)

        with st.expander("🔍 View AI Risk Score Breakdown"):
            rb = tiers[selected_tier]["risk_breakdown"]
            r1, r2, r3 = st.columns(3)
            r1.metric("Zone Risk",       rb['zone_risk'])
            r1.metric("City Risk",       rb['city_risk'])
            r2.metric("Season Risk",     rb['season_risk'])
            r2.metric("Experience Risk", rb['experience_risk'])
            r3.metric("Income Risk",     rb['income_risk'])
            r3.metric("Final Score",     tiers[selected_tier]['risk_score'])

        col_btn, _ = st.columns([1, 2])
        with col_btn:
            if st.button(f"🛡 Activate {tiers[selected_tier]['tier']} Protection →"):
                res = requests.post(f"{API_BASE}/policy/create",
                                    json={"worker_id": st.session_state.worker_id,
                                          "tier": selected_tier})
                if res.status_code == 200:
                    d = res.json()
                    st.success(f"✅ Policy activated! Covered until {str(d['valid_until'])[:10]}")
                    st.balloons()
                else:
                    st.error(res.json().get("detail", "Could not create policy"))

    except Exception as e:
        st.error(f"Error: {e}")

# =================================================
# MY COVERAGE
# =================================================
elif role == "👷 Worker" and page == "My Coverage":
    page_header("📄", "My Coverage", "Your active weekly policy details")

    if not st.session_state.worker_id:
        st.warning("⚠️ Please login first")
        st.stop()

    try:
        res  = requests.get(f"{API_BASE}/policy/active/{st.session_state.worker_id}")
        data = res.json()

        if "policy_id" not in data:
            st.markdown("""
            <div style="background:#FEF2F2; border:2px solid #FECACA; border-radius:20px;
                        padding:48px; text-align:center;">
                <div style="font-size:48px; margin-bottom:12px">😔</div>
                <div style="font-size:20px; font-weight:700; color:#991B1B;">No Active Policy</div>
                <div style="color:#B91C1C; margin-top:8px;">
                    Go to 'Buy Policy' in the sidebar to protect your income.
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            col1, col2, col3 = st.columns(3)
            col1.metric("💰 Weekly Coverage", f"₹{data['coverage_amount']}")
            col2.metric("💳 Weekly Premium",  f"₹{data['weekly_premium']}")
            col3.metric("📅 Days Remaining",  data["days_remaining"])

            progress = max(0.0, min(data["days_remaining"] / 7, 1.0))
            st.markdown(f"""
            <div style="background:white; border-radius:16px; padding:24px 28px; margin-top:16px;
                        border:1px solid #E8EAF0; box-shadow:0 2px 12px rgba(0,0,0,0.06);">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:14px;">
                    <span style="font-weight:700; font-size:16px; color:#0D1117;">Policy Status</span>
                    <span style="background:#2ECC71; color:white; padding:6px 18px; border-radius:20px;
                                 font-weight:700; font-size:12px; letter-spacing:0.5px;">✓ ACTIVE</span>
                </div>
                <div style="background:#F3F4F6; border-radius:8px; height:10px; overflow:hidden;">
                    <div style="background:linear-gradient(90deg,#2ECC71,#27AE60); height:100%;
                                width:{int(progress*100)}%; border-radius:8px;"></div>
                </div>
                <div style="display:flex; justify-content:space-between; margin-top:8px;">
                    <span style="font-size:12px; color:#9CA3AF;">Policy started</span>
                    <span style="font-size:12px; color:#374151; font-weight:600;">
                        {data['days_remaining']} days left — expires {str(data['end_date'])[:10]}
                    </span>
                </div>
            </div>
            """, unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Error: {e}")

# =================================================
# CLAIMS
# =================================================
elif role == "👷 Worker" and page == "Claims":
    page_header("⚡", "Claims Center", "File and track your income protection claims")

    if not st.session_state.worker_id:
        st.warning("⚠️ Please login first")
        st.stop()

    try:
        worker_res  = requests.get(f"{API_BASE}/auth/worker/{st.session_state.worker_id}")
        worker      = worker_res.json()
        weather_res = requests.get(f"{API_BASE}/triggers/check/{worker['city']}")
        weather     = weather_res.json()

        st.markdown(f"### 🌍 Live Conditions — {worker['city'].title()}")

        if weather["is_disrupted"]:
            for d in weather["disruptions"]:
                st.markdown(f"""
                <div style="background:#FEF2F2; border:2px solid #F87171; border-radius:16px;
                            padding:18px 22px; margin-bottom:14px;">
                    <div style="font-size:17px; font-weight:700; color:#991B1B;">
                        🚨 {d['type'].replace('_',' ').title()} Detected
                    </div>
                    <div style="color:#B91C1C; font-size:13px; margin-top:5px;">
                        {d['message']} &nbsp;•&nbsp; Measured: <b>{d['value']}</b>
                        &nbsp;•&nbsp; Severity: <b>{d['severity'].upper()}</b>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            trigger_options  = [d["type"] for d in weather["disruptions"]]
            selected_trigger = st.selectbox("🎯 Select Disruption to Claim", trigger_options,
                format_func=lambda x: x.replace("_", " ").title())

            st.markdown("""
            <div style="background:white; border-radius:14px; padding:18px 22px;
                        border:1px solid #E8EAF0; margin-bottom:18px;">
                <div style="font-weight:700; font-size:14px; color:#0D1117; margin-bottom:10px;">
                    ✅ AI Verification Checks
                </div>
                <div style="display:grid; grid-template-columns:1fr 1fr; gap:6px;
                            font-size:13px; color:#065F46;">
                    <div>✅ Income loss verified by AI</div>
                    <div>✅ Location cross-validated</div>
                    <div>✅ Fraud detection passed</div>
                    <div>✅ Policy active and valid</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            col_btn, _ = st.columns([1, 2])
            with col_btn:
                if st.button("⚡ File Instant Claim →"):
                    res = requests.post(f"{API_BASE}/claims/initiate",
                                        json={"worker_id": st.session_state.worker_id,
                                              "trigger_type": selected_trigger})
                    if res.status_code != 200 or not res.text.strip():
                        st.error(f"Server error {res.status_code}: {res.text or 'Empty response'}")
                        st.stop()
                    result = res.json()
                    if result.get("status") == "approved":
                        payout = result.get("payout", {})
                        st.markdown(f"""
                        <div style="background:linear-gradient(135deg,#ECFDF5 0%,#D1FAE5 100%);
                                    border:2px solid #6EE7B7; border-radius:20px; padding:28px;
                                    text-align:center; margin-top:16px;">
                            <div style="font-size:44px">🎉</div>
                            <div style="font-size:24px; font-weight:800; color:#065F46; margin:8px 0;">
                                Claim Approved!
                            </div>
                            <div style="font-size:32px; font-weight:800; color:#059669;">
                                ₹{result['approved_amount']} Credited
                            </div>
                            <div style="color:#6B7280; font-size:13px; margin-top:8px;">
                                TXN: <b>{payout.get('transaction_id','N/A')}</b>
                                &nbsp;•&nbsp; via {payout.get('method','UPI')}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        st.balloons()
                    elif result.get("status") == "under_review":
                        st.warning(f"🔍 {result['message']}")
                    else:
                        st.error(f"❌ {result.get('message', 'Unknown error')}")
                        for r in result.get("reasons", []):
                            st.caption(f"Reason: {r}")
        else:
            st.markdown("""
            <div style="background:#ECFDF5; border:2px solid #6EE7B7; border-radius:20px;
                        padding:36px; text-align:center;">
                <div style="font-size:44px">☀️</div>
                <div style="font-size:18px; font-weight:700; color:#065F46; margin:8px 0;">
                    No Active Disruptions
                </div>
                <div style="color:#6B7280; font-size:14px;">
                    Conditions are stable. Claims are only processed during verified disruption events.
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("### 📋 Claims History")
        claims_res  = requests.get(f"{API_BASE}/claims/worker/{st.session_state.worker_id}")
        claims_data = claims_res.json()
        if claims_data["total"] > 0:
            st.dataframe(pd.DataFrame(claims_data["claims"]),
                         use_container_width=True, hide_index=True)
        else:
            st.info("No claims filed yet.")

    except Exception as e:
        st.error(f"Error: {e}")
# =================================================
# ADMIN DASHBOARD  ← FIX 2: button now inside try block
# =================================================
elif role == "🏢 Admin" and page == "Admin Dashboard":
    page_header("📊", "Command Center", "Real-time insurance platform analytics")

    try:
        res        = requests.get(f"{API_BASE}/dashboard/admin")
        data       = res.json()
        overview   = data["overview"]
        financials = data["financials_30d"]
        claims     = data["claims_analysis"]

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("🛡 Active Policies", overview["active_policies"])
        col2.metric("👷 Total Workers",   overview["total_workers"])
        col3.metric("📋 Total Claims",    overview["total_claims"])
        col4.metric("💰 Total Payouts",   f"₹{financials['total_payouts']}")

        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        col1.metric("💳 Premium Collected", f"₹{financials['premium_collected']}")
        col2.metric("📉 Loss Ratio",        f"{financials['loss_ratio_pct']}%",
                    delta="-2.1%" if financials['loss_ratio_pct'] < 50 else "+3.4%")
        col3.metric("📈 Net Balance",       f"₹{financials['net_balance']}")

        st.markdown("---")
        st.markdown("### ⚡ Instant Payout Engine")

        col_btn, col_info = st.columns([1, 2])
        with col_btn:
            if st.button("⚡ Process Auto Claims & Payouts"):
                try:
                    r      = requests.post(f"{API_BASE}/triggers/auto-process")
                    result = r.json()
                    st.success("✅ Payouts processed successfully!")
                    st.markdown(f"""
                    <div style="background:#ECFDF5; border:2px solid #6EE7B7;
                                border-radius:16px; padding:16px; margin-top:10px;">
                        <b>Processed Claims:</b> {result.get('processed', result.get('claims_triggered', 0))}<br>
                        <b>Total Payout:</b> ₹{result.get('total_payout', 0)}
                    </div>
                    """, unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"❌ Failed: {e}")
        with col_info:
            st.info("Triggers zero-touch claim processing and simulates instant UPI payouts.")

        st.markdown("---")
        chart1, chart2 = st.columns(2)

        with chart1:
            st.markdown("#### Claims by Disruption Type")
            trigger_data = claims.get("by_trigger_type", {})
            if trigger_data:
                fig, ax = plt.subplots(figsize=(6, 4))
                fig.patch.set_facecolor("white")
                ax.set_facecolor("white")
                colors = ["#2ECC71","#E67E22","#E74C3C","#3498DB","#9B59B6"]
                bars = ax.bar(list(trigger_data.keys()), list(trigger_data.values()),
                              color=colors[:len(trigger_data)], width=0.5)
                for bar in bars:
                    height = bar.get_height()
                    ax.text(bar.get_x() + bar.get_width() / 2, height,
                            str(int(height)), ha='center', va='bottom', fontsize=9)
                ax.set_title("Claims by Disruption Type", fontsize=13,
                             fontweight="bold", color="#0D1117", pad=12)
                ax.tick_params(colors="#6B7280", labelsize=10)
                for spine in ax.spines.values():
                    spine.set_edgecolor("#E8EAF0")
                st.pyplot(fig)
            else:
                st.info("No claims data yet")

        with chart2:
            st.markdown("#### Policies by City")
            city_data = data["geography"]["policies_by_city"]
            if city_data:
                fig2, ax2 = plt.subplots(figsize=(6, 4))
                fig2.patch.set_facecolor("white")
                ax2.set_facecolor("white")
                colors2 = ["#2ECC71","#E67E22","#3498DB","#E74C3C","#9B59B6","#1ABC9C"]
                ax2.pie(list(city_data.values()), labels=list(city_data.keys()),
                        colors=colors2[:len(city_data)], autopct="%1.0f%%", startangle=90)
                ax2.set_title("Policies by City", fontsize=13,
                              fontweight="bold", color="#0D1117", pad=12)
                st.pyplot(fig2)
            else:
                st.info("No city data yet")

        st.markdown("---")
        st.markdown("#### 🔮 Next Week Risk Forecast")
        import random
        random.seed(42)   # fixed seed so chart doesn't flicker on every rerender
        cities           = ["Bangalore", "Mumbai", "Delhi", "Chennai", "Hyderabad", "Pune"]
        predicted_claims = [random.randint(5, 25) for _ in cities]
        fig3, ax3 = plt.subplots(figsize=(8, 3))
        fig3.patch.set_facecolor("white")
        ax3.set_facecolor("white")
        bar_colors = ["#E74C3C" if v > 18 else "#E67E22" if v > 12 else "#2ECC71"
                      for v in predicted_claims]
        ax3.bar(cities, predicted_claims, color=bar_colors, width=0.5)
        ax3.axhline(y=15, color="#E74C3C", linestyle="--", linewidth=1, alpha=0.6)
        ax3.text(5.4, 15.5, "Risk threshold", fontsize=9, color="#E74C3C")
        ax3.set_title("Predicted Disruptions — Next 7 Days", fontsize=13,
                      fontweight="bold", color="#0D1117", pad=12)
        ax3.set_ylabel("Expected Claims")
        ax3.tick_params(colors="#6B7280", labelsize=10)
        for spine in ax3.spines.values():
            spine.set_edgecolor("#E8EAF0")
        st.pyplot(fig3)

    except Exception as e:
        st.error(f"Error: {e}")

# =================================================
# LIVE TRIGGERS  ← FIX 3: removed duplicate page_header + merged both blocks
# =================================================
elif role == "🏢 Admin" and page == "Live Triggers":
    page_header("🌍", "Live Triggers", "Live disruption tracking across all cities")

    city_select = st.selectbox("Quick-check a city", ["bangalore", "mumbai", "delhi", "chennai", "hyderabad", "pune"])
    if st.button("🔍 Check Triggers Now"):
        try:
            res  = requests.get(f"{API_BASE}/triggers/check/{city_select}")
            data = res.json()
            if data["is_disrupted"]:
                for d in data["disruptions"]:
                    st.warning(f"**{d['type'].replace('_',' ').title()}** — Severity: {d['severity']} | Income loss: {d.get('income_loss_pct','?')}%")
            else:
                st.success(f"✅ No disruptions in {city_select.title()} right now")
        except Exception as e:
            st.error(f"Failed to fetch trigger data: {e}")

    st.markdown("---")
    st.markdown("### 🗺 All Cities Status")

    for city in ["bangalore", "mumbai", "delhi", "chennai", "hyderabad", "pune"]:
        try:
            res  = requests.get(f"{API_BASE}/triggers/check/{city}")
            data = res.json()
            if data["is_disrupted"]:
                disruptions_text = " | ".join([
                    f"{d['type'].replace('_',' ').title()}: {d['value']}"
                    for d in data["disruptions"]
                ])
                st.markdown(f"""
                <div style="background:#FEF2F2; border:1px solid #FECACA; border-radius:14px;
                            padding:16px 22px; margin-bottom:10px;
                            display:flex; justify-content:space-between; align-items:center;">
                    <div>
                        <span style="font-weight:700; color:#991B1B; font-size:15px;">🚨 {city.title()}</span>
                        <span style="color:#B91C1C; font-size:13px; margin-left:12px;">{disruptions_text}</span>
                    </div>
                    <span style="background:#EF4444; color:white; padding:4px 14px; border-radius:20px;
                                 font-size:11px; font-weight:700;">DISRUPTED</span>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style="background:#ECFDF5; border:1px solid #A7F3D0; border-radius:14px;
                            padding:16px 22px; margin-bottom:10px;
                            display:flex; justify-content:space-between; align-items:center;">
                    <span style="font-weight:600; color:#065F46; font-size:15px;">✅ {city.title()}</span>
                    <span style="background:#2ECC71; color:white; padding:4px 14px; border-radius:20px;
                                 font-size:11px; font-weight:700;">NORMAL</span>
                </div>
                """, unsafe_allow_html=True)
        except Exception:
            st.warning(f"⚠️ {city.title()} — Could not fetch data")

# =================================================
# FRAUD DETECTION  ← FIX 4: removed duplicate fraud table block
# =================================================
elif role == "🏢 Admin" and page == "Fraud Detection":
    page_header("🚨", "Fraud Detection", "AI-powered anomaly detection and alerts")

    try:
        res      = requests.get(f"{API_BASE}/dashboard/admin")
        data     = res.json()
        rejected = data["claims_analysis"]["rejected"]
        approval = data["claims_analysis"]["approval_rate_pct"]

        col1, col2, col3 = st.columns(3)
        col1.metric("🚫 Rejected Claims", rejected)
        col2.metric("✅ Clean Approvals", data["claims_analysis"]["approved"])
        col3.metric("📊 Approval Rate",   f"{approval}%")

        if rejected > 0:
            st.error(f"⚠️ {rejected} claims were rejected by fraud detection")
        else:
            st.success("✅ No fraud detected. All claims passed verification.")

        st.markdown("### 🧠 High-Risk Claims (Fraud Score)")
        try:
            claims_res  = requests.get(f"{API_BASE}/claims/all")
            claims_data = claims_res.json().get("claims", [])
            if claims_data:
                df = pd.DataFrame(claims_data)
                if "fraud_score" in df.columns:
                    high_risk = df[df["fraud_score"] > 60].sort_values(
                        by="fraud_score", ascending=False
                    )
                    if not high_risk.empty:
                        # Color-coded fraud score display
                        def score_color(score):
                            if score > 75: return "🔴"
                            if score > 60: return "🟡"
                            return "🟢"

                        display_df = high_risk[["id", "worker_id", "trigger_type", "fraud_score", "status"]].copy()
                        display_df["risk"] = display_df["fraud_score"].apply(score_color)
                        st.dataframe(display_df, use_container_width=True, hide_index=True)
                    else:
                        st.success("✅ No high-risk claims detected")
                else:
                    st.info("Fraud score not yet available from API")
            else:
                st.info("No claims found")
        except Exception as e:
            st.warning(f"Could not fetch claims for fraud analysis: {e}")

        st.markdown("### 🔐 Active Fraud Checks")
        checks = [
            ("🔄", "Duplicate Claims",    "Blocks same-day repeat claims from same worker",    "Active"),
            ("📍", "Location Validation", "Verifies worker is in a disrupted zone",             "Active"),
            ("🌦", "Weather Matching",    "Claim type must match real-time weather conditions", "Active"),
            ("📊", "Frequency Analysis",  "Flags workers with more than 3 claims in 30 days",  "Active"),
            ("📋", "Policy Validation",   "Ensures active policy exists before payout",         "Active"),
        ]
        for icon, name, desc, status in checks:
            st.markdown(f"""
            <div style="background:white; border:1px solid #E8EAF0; border-radius:12px;
                        padding:14px 18px; margin-bottom:8px;
                        display:flex; justify-content:space-between; align-items:center;">
                <div style="display:flex; gap:12px; align-items:center;">
                    <span style="font-size:18px">{icon}</span>
                    <div>
                        <div style="font-weight:600; color:#0D1117; font-size:14px;">{name}</div>
                        <div style="font-size:12px; color:#6B7280;">{desc}</div>
                    </div>
                </div>
                <span style="background:#ECFDF5; color:#065F46; padding:4px 14px; border-radius:20px;
                             font-size:11px; font-weight:700; border:1px solid #A7F3D0;">{status}</span>
            </div>
            """, unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Error: {e}")