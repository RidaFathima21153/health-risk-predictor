import streamlit as st
import pandas as pd
import os
import plotly.express as px
from database import get_all_history

st.set_page_config(page_title="Doctor Portal", page_icon="👨‍⚕️", layout="wide")

def load_css():
    if os.path.exists("style.css"):
        with open("style.css") as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
load_css()

if 'user' not in st.session_state:
    st.warning("Please log in first.")
    st.stop()

if st.session_state.get('role') != 'doctor':
    st.error("Access Denied. This portal is restricted to authorized medical personnel.")
    st.stop()

st.title("👨‍⚕️ Doctor Administration Portal")
st.markdown("System-wide aggregated diagnostics and patient risk tracking.")

df = get_all_history()

if df.empty:
    st.info("No patient data available in the system yet.")
    st.stop()

col1, col2, col3 = st.columns(3)
total_patients = df['username'].nunique()
high_risk = len(df[df['risk_pred'] == 'High'])
avg_health = df['health_score'].mean()

col1.metric("Total Patients Active", total_patients)
col2.metric("High Risk Predictors", high_risk, delta_color="inverse")
col3.metric("System Avg Health Score", f"{avg_health:.1f}/100")

st.divider()

st.subheader("Global Risk Distribution")
pie_fig = px.pie(df, names='risk_pred', title="Risk Assessment Breakdown", color_discrete_sequence=px.colors.qualitative.Pastel)
pie_fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="white")
st.plotly_chart(pie_fig, use_container_width=True)

st.subheader("Patient Directory (Searchable)")
st.dataframe(df, use_container_width=True)
