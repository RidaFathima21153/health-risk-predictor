import streamlit as st
import os
import plotly.express as px
import plotly.graph_objects as go
from fpdf import FPDF
import base64
from database import get_user_history, get_user_profile

st.set_page_config(page_title="Trend History", page_icon="📈", layout="wide")

def load_css():
    if os.path.exists("style.css"):
        with open("style.css") as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
load_css()

if 'user' not in st.session_state:
    st.warning("Please log in first.")
    st.stop()

st.title("Historical Trend Analysis 📈")
user = st.session_state['user']
df = get_user_history(user)
profile = get_user_profile(user)

if df.empty:
    st.info("You haven't run any diagnostics yet. Head to the Dashboard to get started!")
else:
    st.subheader("Your Health Score Over Time")
    fig_score = px.line(df, x='timestamp', y='health_score', markers=True)
    fig_score.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="white")
    st.plotly_chart(fig_score, use_container_width=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Vitals Tracking")
        fig_vitals = px.line(df, x='timestamp', y=['bp', 'sugar', 'cholesterol'])
        fig_vitals.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="white", legend_title="Metrics")
        st.plotly_chart(fig_vitals, use_container_width=True)
        
    with col2:
        st.subheader("BMI Tracking vs Target")
        fig_bmi = go.Figure()
        fig_bmi.add_trace(go.Scatter(x=df['timestamp'], y=df['bmi'], mode='lines+markers', name='Actual BMI', line=dict(color='#8b5cf6')))
        if profile and profile['target_bmi']:
            fig_bmi.add_trace(go.Scatter(x=df['timestamp'], y=[profile['target_bmi']]*len(df), mode='lines', name='Target', line=dict(color='#10b981', dash='dash')))
        fig_bmi.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="white")
        st.plotly_chart(fig_bmi, use_container_width=True)

    st.subheader("Raw History")
    st.dataframe(df.drop(columns=['id', 'username']), use_container_width=True)
    
    st.divider()
    st.subheader("Export Medical Report")
    st.markdown("Download a PDF summary of your latest records to share with your physician.")
    
    if st.button("📄 Generate PDF Report", type="primary"):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt=f"Medical Trends Report - {user}", ln=1, align='C')
        pdf.cell(200, 10, txt=f"Latest Health Score: {df.iloc[-1]['health_score']}", ln=2, align='L')
        pdf.cell(200, 10, txt=f"Total Records: {len(df)}", ln=3, align='L')
        
        pdf.ln(10)
        pdf.set_font("Arial", 'B', 10)
        pdf.cell(50, 10, "Date", 1)
        pdf.cell(30, 10, "BMI", 1)
        pdf.cell(30, 10, "BP", 1)
        pdf.cell(30, 10, "Risk", 1)
        pdf.ln()
        
        pdf.set_font("Arial", '', 10)
        # Limit to last 10 records for the PDF table
        for idx, row in df.tail(10).iterrows():
            pdf.cell(50, 10, str(row['timestamp'].date()), 1)
            pdf.cell(30, 10, str(row['bmi']), 1)
            pdf.cell(30, 10, str(row['bp']), 1)
            pdf.cell(30, 10, str(row['risk_pred']), 1)
            pdf.ln()
            
        pdf_output = pdf.output(dest="S").encode("latin1")
        b64 = base64.b64encode(pdf_output).decode()
        href = f'<a href="data:application/pdf;base64,{b64}" download="Health_Report_{user}.pdf">⬇️ Click here to download PDF</a>'
        st.markdown(href, unsafe_allow_html=True)
