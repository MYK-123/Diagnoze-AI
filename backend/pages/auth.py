import streamlit as st
from utils.api_connect import get_api_client
from utils.auth import login_user, register_user
import time

_GENDER_MAP = {
    "Prefer not to say": "prefer_not_to_say",
    "Male": "male",
    "Female": "female",
    "Other": "other",
}

def render_landing_page(router):
    """Landing page for unauthenticated users"""
    st.title("🏥 Diagnoze AI")
    st.subheader("Intelligent Symptom Analysis & Disease Prediction")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.image("https://via.placeholder.com/400x250?text=AI+Healthcare", use_column_width=True)
        st.markdown("""
        ### How It Works
        1. **Describe your symptoms** in natural language
        2. **AI analyzes** symptom patterns
        3. **Get possible conditions** with confidence scores
        4. **Learn about diseases** with educational content
        """)
    
    with col2:
        st.markdown("""
        ### Key Features
        ✅ **AI-Powered Analysis** - Advanced machine learning models  
        ✅ **Educational Focus** - Learn about symptom-disease relationships  
        ✅ **Safety First** - Clear disclaimers & emergency warnings  
        ✅ **Privacy Protected** - Your data is secure and private  
        ✅ **User-Friendly** - Simple, intuitive interface  
        
        ### Get Started
        """)
        
        if st.button("Login to Continue", type="primary", use_container_width=True):
            router.redirect(*router.build("login"))
        
        if st.button("Create New Account", use_container_width=True):
            router.redirect(*router.build("register"))
        
        st.markdown("---")
        st.markdown("""
        **⚠️ Important Disclaimer**  
        This tool is for educational purposes only and does not provide medical diagnosis.  
        Always consult a healthcare professional for medical advice.
        """)

def render_login_page(router):
    """Login page"""
    st.title("🔐 Login to Diagnoze AI")
    
    with st.form("login_form"):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        remember_me = st.checkbox("Remember me")
        
        col1, col2 = st.columns(2)
        with col1:
            submit = st.form_submit_button("Login", type="primary", use_container_width=True)
        with col2:
            if st.form_submit_button("Cancel", use_container_width=True):
                router.redirect(*router.build("home"))
        
        if submit:
            if not email or not password:
                st.error("Please enter both email and password")
            else:
                with st.spinner("Logging in..."):
                    api = get_api_client()
                    response = api.login(email, password)
                    
                    if response.get("success"):
                        login_user(response["data"]["token"], response["data"]["user"])
                        st.success("Login successful!")
                        router.redirect(*router.build("dashboard"))
                    else:
                        st.error(response.get("message", "Login failed"))
    
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Forgot Password?"):
            st.info("Password reset feature coming soon")
    with col2:
        if st.button("Create New Account"):
            router.redirect(*router.build("register"))

def render_register_page(router):
    """Registration page"""
    st.title("📝 Create New Account")
    
    with st.form("register_form"):
        col1, col2 = st.columns(2)
        with col1:
            first_name = st.text_input("First Name")
            email = st.text_input("Email")
            age = st.number_input("Age", min_value=1, max_value=120, value=25)
        with col2:
            last_name = st.text_input("Last Name")
            password = st.text_input("Password", type="password")
            confirm_password = st.text_input("Confirm Password", type="password")
        
        gender_label = st.selectbox("Gender", ["Prefer not to say", "Male", "Female", "Other"])
        
        st.markdown("#### Account Type")
        account_type = st.radio(
            "Select account type:",
            ["General User", "Medical Student"],
            horizontal=True
        )
        
        agree_terms = st.checkbox("I agree to the Terms of Service and Privacy Policy")
        
        col1, col2 = st.columns(2)
        with col1:
            submit = st.form_submit_button("Create Account", type="primary", use_container_width=True)
        with col2:
            if st.form_submit_button("Cancel", use_container_width=True):
                router.redirect(*router.build("home"))
        
        if submit:
            # Validation
            errors = []
            if not all([first_name, last_name, email, password, confirm_password]):
                errors.append("All fields are required")
            if password != confirm_password:
                errors.append("Passwords do not match")
            if len(password) < 8:
                errors.append("Password must be at least 8 characters")
            if not agree_terms:
                errors.append("You must agree to the terms")
            
            if errors:
                for error in errors:
                    st.error(error)
            else:
                with st.spinner("Creating account..."):
                    user_data = {
                        "first_name": first_name,
                        "last_name": last_name,
                        "email": email,
                        "password": password,
                        "age": int(age),
                        "gender": _GENDER_MAP.get(gender_label, "prefer_not_to_say"),
                        "account_type": "medical_student" if account_type == "Medical Student" else "user"
                    }
                    
                    api = get_api_client()
                    print(user_data)
                    time.sleep(2)
                    response = api.register(user_data)
                    
                    if response.get("success"):
                        st.success("Account created successfully! Please login.")
                        time.sleep(2)
                        router.redirect(*router.build("login"))
                    else:
                        st.error(response.get("message", "Registration failed"))
    
    st.markdown("---")
    st.markdown("Already have an account?")
    if st.button("Login Here"):
        router.redirect(*router.build("login"))

if __name__ == "__main__":
    render_landing_page(None)

