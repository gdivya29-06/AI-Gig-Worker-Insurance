import streamlit as st
import random
import pandas as pd
import matplotlib.pyplot as plt

# =================================================
# PAGE CONFIG
# =================================================
st.set_page_config(
    page_title="GigShield AI",
    page_icon="🛡",
    layout="wide"
)

# =================================================
# 🎨 OLIVE PREMIUM THEME
# =================================================
st.markdown("""
<style>

/* APP BACKGROUND */
.stApp {
    background-color: #EEE8D5;
    color: #4A4F1F;
}

/* SIDEBAR */
section[data-testid="stSidebar"] {
    background-color: #D9D2B6;
}

/* TEXT */
h1, h2, h3, h4, p, label {
    color: #4A4F1F !important;
}

/* METRIC CARDS */
div[data-testid="metric-container"] {
    background-color: #A8B07A;
    padding: 16px;
    border-radius: 14px;
}

/* BUTTONS */
.stButton > button {
    background-color: #4A4F1F;
    color: white;
    border-radius: 12px;
    border: none;
    padding: 0.6rem 1.2rem;
    font-weight: 600;
}

.stButton > button:hover {
    background-color: #3A3F17;
    color: white;
}

/* SELECT BOX */
.stSelectbox > div > div {
    background-color: #A8B07A;
    color: #4A4F1F;
    border-radius: 10px;
}

/* RADIO TEXT */
.stRadio label {
    color: #4A4F1F !important;
}

</style>
""", unsafe_allow_html=True)

# =================================================
# SIDEBAR
# =================================================
st.sidebar.title("🛡 GigShield AI")
st.sidebar.caption("Income Protection for Gig Workers")

role = st.sidebar.radio(
    "Login as",
    ["👷 Worker", "🏢 Admin"]
)

if role == "👷 Worker":
    page = st.sidebar.selectbox(
        "Menu",
        ["Dashboard", "Buy Policy", "My Coverage", "Claims"]
    )
else:
    page = st.sidebar.selectbox(
        "Menu",
        ["Analytics", "Risk Monitor", "Fraud Alerts"]
    )

# =================================================
# 👷 WORKER DASHBOARD
# =================================================
if role == "👷 Worker" and page == "Dashboard":

    st.title("👷 Worker Dashboard")

    risk_score = random.randint(20, 90)
    premium = 29 + risk_score // 10

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("AI Risk Score", f"{risk_score}%")
    col2.metric("Weekly Coverage", "₹3000")
    col3.metric("Dynamic Premium", f"₹{premium}/week")
    col4.metric("Earnings Protected", "₹1200")

    st.progress(risk_score)

    st.subheader("🌦 Live Conditions")

    weather = random.choice(
        ["Heavy Rain", "Heatwave", "Severe Pollution", "Normal"]
    )

    if weather == "Heavy Rain":
        st.warning("☔ Heavy rain expected — deliveries may drop")
    elif weather == "Heatwave":
        st.error("🌡 Extreme heat advisory issued")
    elif weather == "Severe Pollution":
        st.warning("🌫 Hazardous air quality detected")
    else:
        st.success("☀ Conditions stable")

# =================================================
# 👷 BUY POLICY
# =================================================
elif role == "👷 Worker" and page == "Buy Policy":

    st.title("💳 Weekly Insurance Plans")

    plan = st.radio(
        "Select Plan",
        [
            "Basic — ₹29/week",
            "Standard — ₹49/week",
            "Premium — ₹79/week"
        ]
    )

    if st.button("Activate Protection"):
        st.success("Coverage Activated 🎉")
        st.balloons()

# =================================================
# 👷 MY COVERAGE
# =================================================
elif role == "👷 Worker" and page == "My Coverage":

    st.title("📄 Active Coverage")

    col1, col2 = st.columns(2)

    col1.metric("Weekly Coverage", "₹3000")
    col2.metric("Protected Earnings", "₹1200")

    st.success("Status: ACTIVE")
    st.progress(75)

# =================================================
# 👷 CLAIMS
# =================================================
elif role == "👷 Worker" and page == "Claims":

    st.title("⚡ Automated Claim Processing")

    disruption = random.choice(
        ["Extreme Heat", "Heavy Rain", "Severe Pollution"]
    )

    st.warning(f"Disruption Detected: {disruption}")

    st.write("✔ AI verified income loss")
    st.write("✔ Location validated")
    st.write("✔ No fraud detected")

    if st.button("Process Instant Payout"):

        payout = random.randint(500, 1500)

        st.success(f"₹{payout} credited instantly ✅")
        st.info("Transaction ID: TXN" + str(random.randint(10000,99999)))
        st.balloons()

# =================================================
# 🏢 ADMIN ANALYTICS
# =================================================
elif role == "🏢 Admin" and page == "Analytics":

    st.title("📊 Insurance Command Center")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Active Policies", "1,240")
    col2.metric("Weekly Claims", "83")
    col3.metric("Fraud Alerts", "6")
    col4.metric("Total Payout", "₹4.2L")

    # ---------- BAR CHART ----------
    st.subheader("Claim Distribution")

    data = pd.DataFrame({
        "Cause": ["Heat", "Pollution", "Rain"],
        "Claims": [25, 13, 45]
    })

    fig, ax = plt.subplots()
    fig.patch.set_facecolor("#EEE8D5")
    ax.set_facecolor("#EEE8D5")

    ax.bar(data["Cause"], data["Claims"], color="#A8B07A")

    ax.set_title("Claims by Disruption Type", color="#4A4F1F")
    ax.tick_params(colors="#4A4F1F")

    st.pyplot(fig)

    # ---------- LINE CHART ----------
    st.subheader("Next Week Prediction")

    pred = pd.DataFrame({
        "Day": [1, 2, 3, 4],
        "Predicted Claims": [60, 75, 90, 110]
    })

    fig2, ax2 = plt.subplots()
    fig2.patch.set_facecolor("#EEE8D5")
    ax2.set_facecolor("#EEE8D5")

    ax2.plot(
        pred["Day"],
        pred["Predicted Claims"],
        marker="o",
        color="#4A4F1F"
    )

    ax2.set_title("Projected Claims Trend", color="#4A4F1F")
    ax2.tick_params(colors="#4A4F1F")

    st.pyplot(fig2)

# =================================================
# 🏢 RISK MONITOR
# =================================================
elif role == "🏢 Admin" and page == "Risk Monitor":

    st.title("🌍 Zone Risk Monitoring")

    st.info("High disruption probability in coastal regions")

# =================================================
# 🏢 FRAUD ALERTS
# =================================================
elif role == "🏢 Admin" and page == "Fraud Alerts":

    st.title("🚨 Fraud Detection System")

    st.error("GPS spoofing suspected — User ID 7821")
    st.warning("Duplicate claims detected — User ID 4412")
    st.success("Auto-block enabled for high-risk accounts")
