import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.figure_factory as ff
from datetime import datetime, timedelta
from utils.auth import check_authentication
from utils.api_connect import get_api_client

def render_admin_page():
    if not check_authentication():
        return

    st.set_page_config(page_title="Admin Dashboard", layout="wide")
    api = get_api_client()

    st.sidebar.title("Navigation")
    dashboard_type = st.sidebar.radio("Select Dashboard", ["Admin Dashboard", "User Dashboard"])

    if st.button("Home"):
        st.experimental_set_query_params(page="dashboard")

    st.subheader("Navigation")
    st.write("Use the buttons below to navigate to different sections:")

    # Dynamically generate buttons for all pages
    pages = [
        "about", "admin", "auth", "chat", "dashboard", "education", "emergency", "errors", "faq", "history", "medical_student", "profile", "public", "safety", "tracker"
    ]

    cols = st.columns(3)  # Organize buttons into 3 columns
    for idx, page in enumerate(pages):
        with cols[idx % 3]:
            if st.button(page.capitalize()):
                st.experimental_set_query_params(page=page)

    if dashboard_type == "Admin Dashboard":
        render_admin_dashboard(api)
    else:
        render_user_dashboard(api)

def render_admin_dashboard(api):
    st.title("Admin Dashboard")
    st.write("Welcome to the Admin Dashboard. Manage users, content, and system settings here.")
    # Example content
    st.subheader("Admin Metrics")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Users", "150")
    with col2:
        st.metric("Active Admins", "5")

def render_user_dashboard(api):
    st.title("User Dashboard")
    st.write("Welcome to the User Dashboard. View your stats and insights here.")
    # Example content
    st.subheader("User Metrics")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Chats", "12")
    with col2:
        st.metric("Symptoms Tracked", "24")

if __name__ == "__main__":
    st.session_state["logged_in"] = True
    st.session_state["account_type"] = "admin"
    render_admin_page()