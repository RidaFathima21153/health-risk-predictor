import streamlit as st
import pandas as pd
import os
import plotly.express as px
from model import predict_risk, calc_health_score

st.set_page_config(page_title="Report Analyzer", page_icon="📁", layout="wide")

def load_css():
    if os.path.exists("style.css"):
        with open("style.css") as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
load_css()

if 'user' not in st.session_state:
    st.warning("Please log in first.")
    st.stop()

st.title("Batch Report Analyzer 📁")
st.markdown("Upload a CSV file containing patient health records to batch-process predictions using the active Random Forest Model.")

uploaded_file = st.file_uploader("Upload CSV", type=['csv'])

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)
        
        required = ['age', 'bp', 'sugar', 'cholesterol']
        if all(col in df.columns for col in required):
            st.success("CSV Load Successful! Running batch inference...")
            
            results = []
            health_scores = []
            
            for index, row in df.iterrows():
                risk, prob = predict_risk(row['age'], row['bp'], row['sugar'], row['cholesterol'], model_name="Random Forest")
                # Dummy BMI of 24 to isolate effects of blood metrics on health score
                h_score = calc_health_score(24, row['bp'], row['sugar'], row['cholesterol'])  
                results.append(risk)
                health_scores.append(h_score)
                
            df['AI_Risk_Prediction'] = results
            df['AI_Health_Score'] = health_scores
            
            st.dataframe(df.style.applymap(lambda x: "background-color: rgba(220,53,69,0.3)" if x == "High" else "", subset=['AI_Risk_Prediction']), use_container_width=True)
            
            c1, c2 = st.columns(2)
            with c1:
                high_risk_count = (df['AI_Risk_Prediction'] == "High").sum()
                st.metric("Critical Alerts (High Risk Patients)", high_risk_count, delta_color="inverse")
                
                csv_data = df.to_csv(index=False).encode('utf-8')
                st.download_button("📥 Download Annotated CSV", data=csv_data, file_name="ai_annotated_reports.csv", mime="text/csv", type="primary")

            with c2:
                pie_fig = px.pie(df, names='AI_Risk_Prediction', title="Batch Risk Distribution", color_discrete_sequence=px.colors.qualitative.Pastel)
                pie_fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="white", height=300)
                st.plotly_chart(pie_fig, use_container_width=True)
            
        else:
            st.error(f"CSV must contain the following columns: {required}")
            
    except Exception as e:
        st.error(f"Error processing file: {e}")
