import streamlit as st
from streamlit_router import StreamlitRouter
import streamlit_router
from utils.api_connect import get_api_client
from datetime import datetime, timedelta

def render_dashboard(router: StreamlitRouter):

    with st.container(vertical_alignment="center"):
        col1, col2 = st.columns([9,1])
        with col2:
            if st.button("Log Out"):
                router.redirect(*router.build("logout"))
    
    
    st.title("User Dashboard")
    st.write("Welcome to your dashboard. Here you can view your health insights and recent activity.")

    api = get_api_client()

    # Example metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Chats", "12", "+2 this week")
    with col2:
        st.metric("Accuracy Rate", "87%", "+3%")
    with col3:
        st.metric("Symptoms Tracked", "24", "+4 this month")

    st.subheader("Navigation")
    st.write("Use the buttons below to navigate to different sections:")

    # Dynamically generate buttons for all pages
    pages = [
        ("About", "about"),
        ("Admin", "admin"),
        ("Chat", "chat"),
        ("Education", "education"),
        ("Emergency", "emergency"),
        ("FAQ", "faq"),
        # ("History", "history"),
        # ("Medical Student", "medical_student"),
        ("Profile", "profile"),
        ("Contact", "public"),
        ("Safety", "safety"),
        ("Tracker", "tracker"),
    ]
    # pages = [
    #     "about", "admin", "auth", "chat", "dashboard", "education", "emergency", "faq", "history", "medical_student", "profile", "public", "safety", "tracker"
    # ]

    cols = st.columns(3)  # Organize buttons into 3 columns
    for idx, (page_name, rout) in enumerate(pages):
        with cols[idx % 3]:
            if st.button(page_name, key=f"nav_{rout}"):
                try:
                    router.redirect(*router.build(rout))
                except Exception as e:
                    st.error(f"Coudn't navigate to: {rout}: {e}")

    st.subheader("Recent Activity")
    st.write("Here are your recent health predictions:")
    # Example data
    recent_predictions = [
        {"date": "2026-02-28", "condition": "Migraine", "confidence": "85%"},
        {"date": "2026-02-27", "condition": "Flu", "confidence": "90%"}
    ]
    for prediction in recent_predictions:
        st.write(f"{prediction['date']}: {prediction['condition']} ({prediction['confidence']})")


