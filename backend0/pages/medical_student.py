import streamlit as st
import pandas as pd
from utils.auth import check_authentication
from utils.api_connect import get_api_client
from streamlit_router import StreamlitRouter

def render_medical_student_page():
    """
    Renders the Medical Student Portal (P25-P29).
    A specialized learning environment for users with the 'medical_student' role.
    """
    if not check_authentication():
        return

    # --- Role-Based Access Control ---
    if st.session_state.get("account_type") != "medical_student":
        st.error("🚫 Access Denied: This portal is for medical students only.")
        st.page_link("app.py", label="Go to Dashboard")
        return

    st.set_page_config(page_title="Medical Student Portal", layout="wide")
    api = get_api_client()

    router = StreamlitRouter()
    register_routes(router)
    router.run()

def render_student_dashboard():
    """P25 - Student Dashboard"""
    st.title("🎓 Medical Student Dashboard")
    user_name = st.session_state.get("user_info", {}).get("full_name", "Student")
    st.header(f"Welcome, {user_name}!")

    # Fetch dashboard data (mocked for now)
    # progress = api.get_student_progress() 
    progress = {"completed_modules": 5, "total_modules": 20, "badges": ["Quick Learner", "Case Master"]}

    st.progress(progress["completed_modules"] / progress["total_modules"])
    st.write(f"You have completed {progress['completed_modules']} out of {progress['total_modules']} modules.")
    
    st.subheader("Your Achievements")
    st.write(" ".join([f"🏅{badge}" for badge in progress["badges"]]))

    st.subheader("Recommended Cases for You")
    # recommended_cases = api.get_recommended_cases()
    # Mock data
    st.info("Case study recommendations coming soon.")


def render_case_studies_library():
    """P26 - Case Studies Library"""
    st.title("📚 Case Studies Library")
    st.info("Interactive case studies coming soon.")

def render_learning_tools():
    """P27 - Learning Tools"""
    st.title("🛠️ Learning Tools")
    st.info("Symptom-disease mapper and differential diagnosis tool coming soon.")

def render_knowledge_assessments():
    """P28 - Knowledge Assessments"""
    st.title("📝 Knowledge Assessments")
    st.info("Timed quizzes and case-based questions coming soon.")

def render_progress_tracking():
    """P29 - Progress Tracking"""
    st.title("📈 Your Progress")
    st.info("Learning path visualization and strength/weakness analysis coming soon.")

def register_routes(router: StreamlitRouter):
    router.map("/medical-student/dashboard", render_student_dashboard)
    router.map("/medical-student/case-studies", render_case_studies_library)
    router.map("/medical-student/learning-tools", render_learning_tools)
    router.map("/medical-student/assessments", render_knowledge_assessments)
    router.map("/medical-student/progress", render_progress_tracking)

if __name__ == "__main__":
    st.session_state["logged_in"] = True
    st.session_state["account_type"] = "medical_student"
    st.session_state["user_info"] = {"email": "student@example.com", "full_name": "Medical Student"}
    render_medical_student_page()
