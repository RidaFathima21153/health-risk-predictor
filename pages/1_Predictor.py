import streamlit as st
import pandas as pd
import random
import time
import os
import plotly.express as px
import plotly.graph_objects as go
from model import predict_risk, calc_bmi, calc_health_score, get_shap_values, data, model_metrics
from database import insert_prediction

st.set_page_config(page_title="Dashboard", page_icon="🏥", layout="wide")

def load_css():
    if os.path.exists("style.css"):
        with open("style.css") as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
load_css()

if 'user' not in st.session_state:
    st.warning("Please log in first.")
    st.stop()

st.title(f"Welcome, {st.session_state['user']} 🏥")
st.markdown("Your Core Diagnostic Dashboard & Live Wearable Data")

# Mock Real-time wearable data & Sync
colA, colB = st.columns([1, 4])
with colA:
    if st.button("🔄 Sync Wearable", use_container_width=True):
        with st.spinner("Connecting to Apple Health / Garmin..."):
            prog = st.progress(0)
            for i in range(100):
                time.sleep(0.01)
                prog.progress(i + 1)
        st.success("Synced!")
        st.session_state['wearable_synced'] = True

if st.session_state.get('wearable_synced', False):
    st.subheader("Live Wearable Feed ⌚ (Synced)")
    m_col1, m_col2, m_col3 = st.columns(3)
    hr_val = random.randint(65, 75)
    steps_val = random.randint(4500, 8000)
    cal_val = random.randint(1800, 2500)
    m_col1.metric("Heart Rate", f"{hr_val} bpm", "-2 bpm")
    m_col2.metric("Steps Today", f"{steps_val} / 10k", "+400")
    m_col3.metric("Calories Burned", f"{cal_val} kcal", "Active")
else:
    st.info("Wearable not synced. Click 'Sync Wearable' to pool data.")

st.divider()

col1, col2 = st.columns([1, 1.5], gap="large")

with col1:
    st.subheader("Diagnostics & Input")
    age = st.number_input("Age", 1, 120, 30)
    weight = st.number_input("Weight (kg)", 20, 250, 70)
    height = st.number_input("Height (cm)", 50, 250, 175)
    bp = st.number_input("Blood Pressure (mmHg)", 50, 250, 120)
    sugar = st.number_input("Blood Sugar (mg/dL)", 50, 400, 90)
    cholesterol = st.number_input("Cholesterol", 100, 400, 180)
    
    selected_model = st.selectbox("AI Engine", ["Logistic Regression", "Random Forest", "XGBoost"], index=1)
    
    if st.button("Run Diagnostics", type="primary"):
        bmi = calc_bmi(weight, height)
        h_score = calc_health_score(bmi, bp, sugar, cholesterol)
        risk, prob = predict_risk(age, bp, sugar, cholesterol, model_name=selected_model)
        
        insert_prediction(st.session_state['user'], age, bp, sugar, cholesterol, bmi, h_score, risk, selected_model)
        
        st.session_state['last_result'] = {
            'risk': risk, 'prob': prob, 'bmi': bmi, 'h_score': h_score,
            'age': age, 'bp': bp, 'sugar': sugar, 'cholesterol': cholesterol, 'model': selected_model
        }

with col2:
    st.subheader("Insight Engine")
    if 'last_result' in st.session_state:
        res = st.session_state['last_result']
        
        r_col1, r_col2, r_col3 = st.columns(3)
        r_col1.metric("Calculated BMI", f"{res['bmi']}")
        r_col2.metric("Health Score (0-100)", f"{res['h_score']}")
        r_col3.metric("Prediction Confidence", f"{res['prob']*100:.1f}%")
        
        # Plotly Gauges
        g_col1, g_col2 = st.columns(2)
        with g_col1:
            fig_score = go.Figure(go.Indicator(
                mode="gauge+number",
                value=res['h_score'],
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "Health Score", 'font': {'color': 'white'}},
                gauge={
                    'axis': {'range': [0, 100]},
                    'bar': {'color': "#38bdf8"},
                    'steps': [
                        {'range': [0, 50], 'color': "rgba(220, 53, 69, 0.5)"},
                        {'range': [50, 80], 'color': "rgba(255, 193, 7, 0.5)"},
                        {'range': [80, 100], 'color': "rgba(25, 135, 84, 0.5)"}],
                }))
            fig_score.update_layout(paper_bgcolor="rgba(0,0,0,0)", font={'color': "white"}, height=200, margin=dict(l=20, r=20, t=30, b=10))
            st.plotly_chart(fig_score, use_container_width=True)
            
        with g_col2:
            fig_conf = go.Figure(go.Indicator(
                mode="gauge+number",
                value=res['prob']*100,
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "Prediction Confidence %", 'font': {'color': 'white'}},
                gauge={'axis': {'range': [0, 100]}, 'bar': {'color': "#8b5cf6"}}
            ))
            fig_conf.update_layout(paper_bgcolor="rgba(0,0,0,0)", font={'color': "white"}, height=200, margin=dict(l=20, r=20, t=30, b=10))
            st.plotly_chart(fig_conf, use_container_width=True)
        
        if res['risk'] == "High":
            st.error(f"### ⚠️ HIGH RISK\nPredicted by {res['model']}")
        elif res['risk'] == "Medium":
            st.warning(f"### ⚡ MEDIUM RISK\nPredicted by {res['model']}")
        else:
            st.success(f"### ✅ LOW RISK\nPredicted by {res['model']}")
            
        st.divider()
        st.subheader("Explainable AI (SHAP Impact)")
        st.markdown("Features pushing right increased the risk score.")
        
        try:
            shap_dict = get_shap_values(res['age'], res['bp'], res['sugar'], res['cholesterol'], model_name=res['model'])
            # Plotly SHAP 
            s_df = pd.DataFrame(list(shap_dict.items()), columns=['Feature', 'SHAP Value'])
            s_df['Color'] = s_df['SHAP Value'].apply(lambda x: '#dc3545' if x > 0 else '#198754')
            fig_shap = px.bar(s_df, x='SHAP Value', y='Feature', orientation='h')
            fig_shap.update_traces(marker_color=s_df['Color'])
            fig_shap.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="white")
            st.plotly_chart(fig_shap, use_container_width=True)
        except Exception as e:
            st.warning(f"SHAP explanation unavailable for this configuration. Error: {e}")
            
    else:
        st.info("Run diagnostics to see your Health Score, BMI, and Explainable AI analysis.")
