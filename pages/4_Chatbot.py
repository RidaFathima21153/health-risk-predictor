import streamlit as st
import time
import os

st.set_page_config(page_title="AI Healthcare Assistant", page_icon="💬", layout="wide")

def load_css():
    if os.path.exists("style.css"):
        with open("style.css") as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
load_css()

if 'user' not in st.session_state:
    st.warning("Please log in first.")
    st.stop()

st.title("AI Healthcare Assistant 💬")
st.markdown("Ask general health questions. For example: *'How to reduce cholesterol'* or *'Tips for blood pressure'*")

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello! I am your rule-based AI Health Assistant. How can I help you improve your stats today?"}
    ]

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Ask a health question..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Basic Rule-Based logic
    response = ""
    prompt_lower = prompt.lower()
    
    if any(word in prompt_lower for word in ["cholesterol", "ldl", "hdl"]):
        response = "To manage cholesterol, focus on eating foods rich in omega-3 fatty acids (like salmon), increase soluble fiber (oats, beans), and eliminate trans fats. High cholesterol over time restricts blood flow and increases heart disease risk."
    elif any(word in prompt_lower for word in ["blood pressure", "bp", "hypertension"]):
        response = "For managing blood pressure: reduce sodium intake to under 1,500mg daily, eat more potassium-rich foods (bananas, sweet potatoes), limit alcohol, and exercise 150 mins/week. Hypertension forces your heart to work harder, increasing stroke risk."
    elif any(word in prompt_lower for word in ["sugar", "glucose", "diabetes"]):
        response = "To stabilize blood sugar, pair carbohydrates with protein or healthy fats. Reduce refined sugars, and consider a 10-minute walk after meals, which significantly blunts glucose spikes. Consistently high sugar can damage blood vessels."
    elif any(word in prompt_lower for word in ["bmi", "weight", "obesity", "fat"]):
        response = "A healthy BMI is generally between 18.5 and 24.9. Lowering BMI through a balanced caloric deficit reduces physical strain on your organs and lowers your baseline risk for type-2 diabetes and heart disease."
    elif any(word in prompt_lower for word in ["risk", "prediction", "high", "heart"]):
        response = "A 'High Risk' prediction means our Random Forest/XGBoost models detected patterns in your vitals reflecting historical cases of cardiovascular stress. You should schedule an in-person consultation with a cardiologist."
    elif any(word in prompt_lower for word in ["sleep", "insomnia", "tired"]):
        response = "Sleep is crucial for recovery. Poor sleep impacts insulin resistance and raises blood pressure. Aim for 7-9 hours by maintaining a cool room, avoiding screens 1 hour prior, and keeping a consistent schedule."
    elif any(word in prompt_lower for word in ["doctor", "appointment", "help"]):
        response = "You can share your generated PDF Medical Report with your primary care provider. Our platform is for screening and guidance, but only a certified doctor can provide a clinical diagnosis."
    else:
        response = "I am a highly advanced diagnostic assistant, but I specialize in metabolic health, heart risk, sleep, and nutrition. Try asking me specifically about your cholesterol, BP, weight goals, or what your risk score means!"
        
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        # Simulate stream typing
        for chunk in response.split(" "):
            full_response += chunk + " "
            time.sleep(0.03)
            message_placeholder.markdown(full_response + "▌")
        message_placeholder.markdown(full_response)
        
    st.session_state.messages.append({"role": "assistant", "content": full_response})
