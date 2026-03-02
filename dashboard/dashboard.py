import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt
import textwrap

st.set_page_config(page_title="OnboardIQ Dashboard", layout="wide")

st.markdown("""
<style>
    body {
        font-family: 'Segoe UI', sans-serif;
    }

    h2 {
        font-weight:600;
    }

    /* TABLE HEADERS */
    thead tr th {
        font-size:20px !important;
        font-weight:800 !important;
        color:#000000 !important;
        text-align:left !important;
    }

    /* TABLE BODY */
    tbody tr td {
        font-size:18px !important;
        color:#111111 !important;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<h1 style='font-size:38px; font-weight:700;'>
📈 OnboardIQ Dashboard
</h1>
""", unsafe_allow_html=True)

BASE_URL = "http://127.0.0.1:8000"

st.sidebar.header("⚙️ Dashboard Settings")
funnel_id = st.sidebar.number_input("Funnel ID", min_value=1, step=1, value=1)
st.sidebar.code("uvicorn main:app --reload")


# API

def get_funnel_steps(funnel_id: int):
    try:
        response = requests.get(f"{BASE_URL}/analytics/funnel/{funnel_id}/steps")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error("Error fetching step data.")
        st.write(e)
        st.stop()

def get_funnel_summary(funnel_id: int):
    try:
        response = requests.get(f"{BASE_URL}/analytics/funnel/{funnel_id}/summary")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error("Error fetching summary data.")
        st.write(e)
        st.stop()

def get_funnel_time(funnel_id: int):
    try:
        response = requests.get(f"{BASE_URL}/analytics/funnel/{funnel_id}/time")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error("Error fetching time analysis.")
        st.write(e)
        st.stop()



if st.sidebar.button("Load Dashboard"):
    st.session_state["load"] = True

if "load" not in st.session_state:
    st.info("👈 Select Funnel ID and click Load Dashboard")
    st.stop()


# Funnel Performance

st.markdown("## 📈 Funnel Performance")

summary_data = get_funnel_summary(funnel_id)

biggest_drop = summary_data.get("biggest_drop_off_step")

st.subheader(" Funnel Summary")

col1, col2, col3 = st.columns(3)

def metric_card(title, value):
    st.markdown(f"""
        <div style="
            background-color:#f7f9fc;
            padding:25px;
            border-radius:12px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.05);
            text-align:center;">
            <p style="font-size:14px; color:gray;">{title}</p>
            <p style="font-size:28px; font-weight:700;">{value}</p>
        </div>
    """, unsafe_allow_html=True)

with col1:
    metric_card("Total Started", f"{summary_data.get('total_started', 0):,}")

with col2:
    metric_card("Total Completed", f"{summary_data.get('total_completed', 0):,}")

with col3:
    metric_card("Overall Conversion", f"{summary_data.get('overall_conversion_percentage', 0)}%")


if biggest_drop:
    st.markdown(f"""
    <div style="
        padding:15px;
        border-radius:10px;
        background-color:#fff4e5;
        border-left:6px solid #ff9800;
        font-weight:600;
        margin-top:15px;
        font-size:18px;">
    <b>Biggest Drop-Off:</b> Step {biggest_drop['step_order']} 
    ({biggest_drop['step_name']}) — 
    {biggest_drop['drop_off_users']} users 
    ({biggest_drop['drop_off_percentage']}%)
    </div>
    """, unsafe_allow_html=True)

st.divider()


# Step Level Analysis

st.markdown("## 📍 Step-Level Analysis")

steps_data = get_funnel_steps(funnel_id)

steps_df = pd.DataFrame(steps_data["steps"])
steps_df["step_name"] = steps_df["step_name"].str.replace("_", " ").str.title()

st.table(steps_df)


# Charts

col1, col2 = st.columns(2)

with col1:
    wrapped_labels = [
        "\n".join(
            textwrap.wrap(
                label,
                width=12,
                break_long_words=False,
                break_on_hyphens=False
            )
        )
        for label in steps_df["step_name"]
    ]

    fig1, ax1 = plt.subplots(figsize=(5,3))
    ax1.bar(wrapped_labels, steps_df["users_at_step"])
    ax1.tick_params(axis='x', labelsize=7)
    ax1.tick_params(axis='y', labelsize=7)
    ax1.set_xlabel("Step", fontsize=12)
    ax1.set_ylabel("Users", fontsize=7)
    plt.xticks(rotation=0)
    plt.tight_layout()
    st.pyplot(fig1)


with col2:
    drop_df = steps_df.dropna(subset=["drop_off_percentage"])

    wrapped_drop_labels = [
        "\n".join(
            textwrap.wrap(
                label,
                width=12,
                break_long_words=False,
                break_on_hyphens=False
            )
        )
        for label in drop_df["step_name"]
    ]

    fig2, ax2 = plt.subplots(figsize=(5,3))
    ax2.bar(wrapped_drop_labels, drop_df["drop_off_percentage"])
    ax2.tick_params(axis='x', labelsize=7)
    ax2.tick_params(axis='y', labelsize=7)
    ax2.set_xlabel("Step", fontsize=12)
    ax2.set_ylabel("Drop-Off %", fontsize=7)
    plt.xticks(rotation=0)
    plt.tight_layout()
    st.pyplot(fig2)

st.divider()


# Process Time Analysis

st.markdown("## ⏱ Process Time Analysis")

time_data = get_funnel_time(funnel_id)

slowest = time_data.get("slowest_transition")

time_df = pd.DataFrame(time_data["time_analysis"])
time_df["step_name"] = time_df["step_name"].str.replace("_", " ").str.title()
time_df["next_step_name"] = time_df["next_step_name"].str.replace("_", " ").str.title()

st.table(time_df)

st.divider()


# Insights

st.markdown("## 🔎 Insights ")

overall_conv = summary_data.get("overall_conversion_percentage")

if overall_conv is not None:
    st.markdown(f"""
    <div style="
        background-color:#eef2ff;
        padding:20px;
        border-radius:10px;
        margin-bottom:15px;
        font-size:18px;">
    <b>Key Insight:</b> Overall conversion is {overall_conv}% — 
    nearly half of users drop before completion.
    </div>
    """, unsafe_allow_html=True)

if slowest:
    st.markdown(f"""
    <div style="
        background-color:#eef2ff;
        padding:20px;
        border-radius:10px;
        margin-bottom:15px;
        font-size:18px;">
    <b>Process Insight:</b> The slowest transition is 
    {slowest['step_name']} → {slowest['next_step_name']} 
    (Avg: {slowest['avg_minutes_to_next_step']} mins).
    </div>
    """, unsafe_allow_html=True)

st.markdown("### 🎯 Strategic Recommendations")
st.markdown("<div style='font-size:18px;'>• Simplify and streamline the highest drop-off step.</div>", unsafe_allow_html=True)
st.markdown("<div style='font-size:18px;'>• Introduce progress indicators and save-and-resume capability.</div>", unsafe_allow_html=True)
st.markdown("<div style='font-size:18px;'>• Reduce delays in the slowest transition through automation or validation optimization.</div>", unsafe_allow_html=True)