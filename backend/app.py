import os
import sys

# Ensure `backend/` is on sys.path BEFORE importing `utils` / `pages`
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import streamlit as st
from utils.auth import check_authentication, logout_user
from pathlib import Path
from streamlit_router import StreamlitRouter

# Page configuration
st.set_page_config(
    page_title="Diagnoze AI",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS
def load_css():
    css_path = Path(__file__).resolve().parent / "styles.css"
    try:
        st.markdown(f"<style>{css_path.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning(f"CSS file not found: {css_path}")

# Initialize router
router = StreamlitRouter()

# Initialize session state with defaults
for key, default in {
    "authenticated": False,
    "user_info": {},
    "user_role": "guest",
    "auth_token": None,
    "current_page": "home"
}.items():
    st.session_state.setdefault(key, default)

# Page definitions (streamlit-router)
@router.map("/")
def home(router: StreamlitRouter):
    if st.session_state.authenticated and check_authentication():
        from pages.dashboard import render_dashboard
        render_dashboard(router)
    else:
        from pages.auth import render_landing_page
        render_landing_page(router)

@router.map("/login")
def login(router: StreamlitRouter):
    from pages.auth import render_login_page
    render_login_page(router)

@router.map("/register")
def register(router: StreamlitRouter):
    from pages.auth import render_register_page
    render_register_page(router)

@router.map("/dashboard")
def dashboard(router: StreamlitRouter):
    if check_authentication():
        from pages.dashboard import render_dashboard
        render_dashboard(router)
    else:
        router.redirect(*router.build("login"))

@router.map("/chat")
def chat(router: StreamlitRouter):
    if check_authentication():
        from pages.chat import render_chat_page
        render_chat_page(router)
    else:
        router.redirect(*router.build("login"))

@router.map("/history")
def history(router: StreamlitRouter):
    if check_authentication():
        from pages.history import render_history_page
        render_history_page(router)
    else:
        router.redirect(*router.build("login"))

@router.map("/profile")
def profile(router: StreamlitRouter):
    if check_authentication():
        from pages.profile import render_profile_page
        render_profile_page(router)
    else:
        router.redirect(*router.build("login"))

@router.map("/tracker")
def tracker(router: StreamlitRouter):
    if check_authentication():
        from pages.tracker import render_tracker_page
        render_tracker_page(router)
    else:
        router.redirect(*router.build("login"))

@router.map("/education")
def education(router: StreamlitRouter):
    if check_authentication():
        from pages.education import render_education_page
        render_education_page(router)
    else:
        router.redirect(*router.build("login"))

@router.map("/admin")
def admin(router: StreamlitRouter):
    if check_authentication() and st.session_state.user_role == "admin":
        from pages.admin import render_admin_page
        render_admin_page(router)
    else:
        st.error("Access denied")
        router.redirect(*router.build("dashboard"))

@router.map("/medical-student")
def medical_student(router: StreamlitRouter):
    if check_authentication() and st.session_state.user_role == "medical_student":
        from pages.medical_student import render_medical_student_page
        render_medical_student_page(router)
    else:
        st.error("Access denied")
        router.redirect(*router.build("dashboard"))

@router.map("/faq")
def faq(router: StreamlitRouter):
    from pages.faq import render_faq_page
    render_faq_page(router)

@router.map("/about")
def about(router: StreamlitRouter):
    from pages.about import render_about_page
    render_about_page(router)

@router.map("/emergency")
def emergency(router: StreamlitRouter):
    from pages.emergency import render_emergency_page
    render_emergency_page(router)

@router.map("/safety")
def safety(router: StreamlitRouter):
    from pages.safety import render_safety_page
    render_safety_page(router)

@router.map("/public")
def public(router: StreamlitRouter):
    from pages.public import render_contact_page
    render_contact_page(router)

# Error pages
@router.map("/404")
def page_not_found(router: StreamlitRouter):
    from pages.errors import render_404_page
    render_404_page(router)

@router.map("/500")
def server_error(router: StreamlitRouter):
    from pages.errors import render_500_page
    render_500_page(router)

@router.map("/logout")
def logout(router: StreamlitRouter):
    logout_user()
    router.redirect(*router.build("home"))

from pages.public import register_routes as register_public_routes
from pages.medical_student import register_routes as register_medical_student_routes

# Register additional routes
register_public_routes(router)
register_medical_student_routes(router)

# Navigation component
def render_navigation():
    if st.session_state.authenticated:
        st.sidebar.title(f"Welcome, {st.session_state.get('user_info', {}).get('full_name', '')}")

        if st.sidebar.button("🏠 Dashboard"):
            router.redirect(*router.build("dashboard"))
        if st.sidebar.button("💬 New Chat"):
            router.redirect(*router.build("chat"))
        if st.sidebar.button("📋 Chat History"):
            router.redirect(*router.build("history"))
        if st.sidebar.button("📈 Symptom Tracker"):
            router.redirect(*router.build("tracker"))
        if st.sidebar.button("📚 Education"):
            router.redirect(*router.build("education"))
        if st.sidebar.button("👤 Profile"):
            router.redirect(*router.build("profile"))

        if st.session_state.user_role == "admin":
            if st.sidebar.button("⚙️ Admin"):
                router.redirect(*router.build("admin"))

        if st.session_state.user_role == "medical_student":
            if st.sidebar.button("🎓 Student Portal"):
                router.redirect(*router.build("medical-student"))

        st.sidebar.markdown("---")
        if st.sidebar.button("🔒 Logout"):
            logout_user()
            st.rerun()

    else:
        if st.sidebar.button("🏠 Homepage"):
            router.redirect(*router.build("home"))
        
        if st.sidebar.button("Contacts"):
            router.redirect(*router.build("public"))
        
        if st.sidebar.button("About Us"):
            router.redirect(*router.build("about"))
        
        if st.sidebar.button("Login"):
            router.redirect(*router.build("login"))

# Main app function
def main():
    # Load CSS
    load_css()

    # Render navigation
    render_navigation()

    # Render current page
    try:
        router.serve()
    except Exception as e:
        # Fallback to 404 or 500
        st.error(f"An error occurred: {e}")
        from pages.errors import render_500_page
        render_500_page(router)

    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style="text-align: center; color: #666; font-size: 0.8em;">
            <a href="/safety">Safety Disclaimer</a> |
            <a href="/about">About & Privacy</a> |
            <a href="/faq">FAQ</a> |
            <a href="/emergency">Emergency</a>
            <br>
            ⚠️ Diagnoze AI is an educational tool, not a diagnostic tool.
            Always consult a healthcare professional for medical advice.
            <br>© 2024 Diagnoze AI
        </div>
        """,
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()