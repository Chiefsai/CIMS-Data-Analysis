import streamlit as st
import pandas as pd
from datetime import datetime
import os

# --- App Config & Styling ---
st.set_page_config(page_title="CIMS Transaction Time Measure", layout="wide", page_icon="📘")

st.markdown("""
<style>
    body {
        background-color: #F4F7FA;
    }
    .main {
        background-color: #F4F7FA;
    }
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    h1, h2, h3 {
        color: #003366;
    }
    .metric {
        background-color: #D6E4FF;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
    }
    .stButton > button {
        background-color: #003366;
        color: white;
        border-radius: 5px;
    }
</style>
""", unsafe_allow_html=True)

# --- Title ---
st.title("📘 CIMS Transaction Time Measure")

# --- Always show name input ---
user_name = st.text_input("👤 Please enter your name to start:", key="username_input")

# --- Stop here if name not entered ---
if not user_name:
    st.warning("Enter your name above to begin.")
    st.stop()

# --- Continue after name is entered ---
sanitized_user = user_name.strip().replace(" ", "_")
log_path = f"cims_time_log_{sanitized_user}.xlsx"

# --- Load or initialize log ---
if os.path.exists(log_path):
    df_log = pd.read_excel(log_path, engine='openpyxl')
else:
    df_log = pd.DataFrame(columns=["User", "CIMS ID", "Start Time", "End Time", "Duration (secs)"])

# --- Session State Setup ---
if "active_entries" not in st.session_state:
    st.session_state.active_entries = []

# --- Tabs ---
tab1, tab2 = st.tabs(["📝 Data Entry", "📊 Analytics & Logs"])

# ===================== TAB 1 =====================
with tab1:
    st.subheader("➕ Enter New CIMS ID")

    cims_id_input = st.text_input("Paste CIMS ID and press Enter")

    if cims_id_input:
        start_time = datetime.now()
        st.session_state.active_entries.append({
            "User": user_name,
            "CIMS ID": cims_id_input.strip(),
            "Start Time": start_time,
            "End Time": None,
            "Duration (secs)": None
        })
        st.toast(f"✅ Start recorded for {cims_id_input.strip()} at {start_time.strftime('%H:%M:%S')}", icon="🕒")

    # Pending Entries
    pending = [e for e in st.session_state.active_entries if e["End Time"] is None]
    if pending:
        st.markdown("### ⏳ Pending Entries")
        for entry in pending:
            st.markdown(
                f"- **{entry['CIMS ID']}** | 🕒 Start: `{entry['Start Time'].strftime('%Y-%m-%d %H:%M:%S')}`"
            )

    # Complete Entry
    if st.button("📤 Process End Time"):
        for entry in st.session_state.active_entries:
            if entry["End Time"] is None:
                end_time = datetime.now()
                duration = (end_time - entry["Start Time"]).total_seconds()

                entry["End Time"] = end_time
                entry["Duration (secs)"] = round(duration, 2)

                df_log = pd.concat([df_log, pd.DataFrame([entry])], ignore_index=True)

                try:
                    df_log.to_excel(log_path, index=False, engine='openpyxl')
                    st.toast(f"📌 ID {entry['CIMS ID']} submitted. Time: {round(duration, 2)}s", icon="✅")
                except Exception as e:
                    st.error(f"❌ Failed to save: {e}")
                break
        else:
            st.info("ℹ️ No pending entries to complete.")

    st.divider()
    with st.expander("📋 View Logged Entries"):
        st.dataframe(df_log, use_container_width=True)

# ===================== TAB 2 =====================
with tab2:
    st.subheader("📊 Time Analysis")

    if not df_log.empty and "Duration (secs)" in df_log.columns:
        df_log["Start Time"] = pd.to_datetime(df_log["Start Time"])
        df_log["End Time"] = pd.to_datetime(df_log["End Time"])

        avg_dur = df_log["Duration (secs)"].mean()
        max_dur = df_log["Duration (secs)"].max()
        min_dur = df_log["Duration (secs)"].min()
        total_txns = len(df_log)

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("⏱️ Average Time", f"{avg_dur:.2f} sec")
        col2.metric("📈 Max Time", f"{max_dur:.2f} sec")
        col3.metric("📉 Min Time", f"{min_dur:.2f} sec")
        col4.metric("🧾 Total Transactions", total_txns)

        st.markdown("### 📈 Time Trend")
        st.line_chart(df_log["Duration (secs)"])

        with st.expander("📄 Raw Data"):
            st.dataframe(df_log, use_container_width=True)
    else:
        st.warning("⚠️ No processed entries available.")
