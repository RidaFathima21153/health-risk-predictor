import streamlit as st
import os
from database import get_user_profile, update_user_profile

st.set_page_config(page_title="Settings & Goals", page_icon="⚙️", layout="wide")

def load_css():
    if os.path.exists("style.css"):
        with open("style.css") as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
load_css()

if 'user' not in st.session_state:
    st.warning("Please log in first.")
    st.stop()

st.title("⚙️ Profile & Goal Settings")
st.markdown("Set your health targets here. These will be overlaid on your Trends chart.")

user = st.session_state['user']
profile = get_user_profile(user)

if not profile:
    st.error("Profile not found.")
    st.stop()

# Doctor portal redirection logic or hide goals for doctors?
if profile['role'] == 'doctor':
    st.info("You are logged in as a Doctor. Target goals are primarily for Patient accounts, but you can still set them for testing.")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Target Metrics")
    new_weight = st.number_input("Target Weight (kg)", min_value=30.0, max_value=300.0, value=float(profile['target_weight']), step=0.5)
    new_bmi = st.number_input("Target BMI", min_value=15.0, max_value=50.0, value=float(profile['target_bmi']), step=0.5)
    
    if st.button("Save Goals", type="primary"):
        update_user_profile(user, new_weight, new_bmi)
        st.success("Goals updated successfully! Check your Trends timeline to see them applied.")

with col2:
    st.subheader("Your Current Targets")
    st.metric("Weight Goal", f"{profile['target_weight']} kg")
    st.metric("BMI Goal", f"{profile['target_bmi']}")
