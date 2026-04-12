import streamlit as st
import os
from database import init_db, create_user, authenticate_user

# Run DB initialization
init_db()

st.set_page_config(page_title="Auth - Enterprise Health", page_icon="🔐", layout="wide")

# Apply custom CSS
def load_css():
    if os.path.exists("style.css"):
        with open("style.css") as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

load_css()

if 'user' in st.session_state:
    role_badge = "👨‍⚕️ Doctor" if st.session_state.get('role') == 'doctor' else "👤 Patient"
    st.success(f"Logged in as {st.session_state['user']} ({role_badge})")
    st.markdown("### 👈 Success! Use the navigation menu on the left to access your Dashboards.")
    
    if st.button("Logout"):
        del st.session_state['user']
        if 'role' in st.session_state:
            del st.session_state['role']
        st.rerun()
else:
    st.title("🔐 Enterprise Health Platform")
    st.markdown("Please log in or register to securely store your medical dashboard history.")

    tab1, tab2 = st.tabs(["Login", "Register"])
    
    with tab1:
        st.subheader("Login to your account")
        l_user = st.text_input("Username", key="l_user")
        l_pass = st.text_input("Password", type="password", key="l_pass")
        if st.button("Login", type="primary"):
            success, role = authenticate_user(l_user, l_pass)
            if success:
                st.session_state['user'] = l_user
                st.session_state['role'] = role
                st.success("Login successful!")
                st.rerun()
            else:
                st.error("Invalid username or password")
                
    with tab2:
        st.subheader("Create an account")
        r_user = st.text_input("Choose Username", key="r_user")
        r_pass = st.text_input("Choose Password", type="password", key="r_pass")
        r_pass2 = st.text_input("Confirm Password", type="password", key="r_pass2")
        r_role = st.selectbox("Role", ["Patient", "Doctor"])
        
        if st.button("Register", type="primary"):
            if r_pass != r_pass2:
                st.error("Passwords do not match!")
            elif len(r_user) < 3:
                st.error("Username too short")
            else:
                db_role = 'doctor' if r_role == 'Doctor' else 'patient'
                if create_user(r_user, r_pass, db_role):
                    st.success("Registration successful! You can now log in.")
                else:
                    st.error("Username already exists!")