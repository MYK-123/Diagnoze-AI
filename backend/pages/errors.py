
import streamlit as st
import time

def render_404_page():
    """
    Renders the 404 Not Found page (P37).
    """
    st.set_page_config(page_title="Page Not Found", layout="centered")
    st.title("😕 404 - Page Not Found")
    st.write("Oops! The page you're looking for doesn't seem to exist.")
    st.image("https://media.giphy.com/media/l2JpT4bQ9C1y7iSgU/giphy.gif", use_column_width=True)
    if st.button("Go to Dashboard"):
        st.switch_page("app.py") # Assumes main router is app.py

def render_500_page():
    """
    Renders the 500 Server Error page (P38).
    """
    st.set_page_config(page_title="Server Error", layout="centered")
    st.title("🔥 500 - Internal Server Error")
    st.write("Sorry, something went wrong on our end. We've been notified and are looking into it.")
    st.image("https://media.giphy.com/media/3o7aD4grHwn87v5F3a/giphy.gif", use_column_width=True)
    if st.button("Retry"):
        st.rerun()

def render_access_denied_page():
    """
    Renders the Access Denied page (P39).
    """
    st.set_page_config(page_title="Access Denied", layout="centered")
    st.title("🚫 403 - Access Denied")
    st.warning("You do not have the necessary permissions to view this page.")
    st.write("If you believe this is an error, please contact your system administrator.")
    if st.button("Go to Dashboard"):
        st.switch_page("app.py")

def render_maintenance_page():
    """
    Renders the Maintenance Mode page (P40).
    """
    st.set_page_config(page_title="Under Maintenance", layout="centered")
    st.title("🛠️ Under Maintenance")
    st.info("Diagnoze AI is currently undergoing scheduled maintenance. We expect to be back online shortly.")
    st.write("Estimated completion time: In a few hours.")
    st.progress(50)

def render_session_expired_page():
    """
    Renders the Session Expired page (P41) and redirects.
    """
    st.set_page_config(page_title="Session Expired", layout="centered")
    st.title("⏳ Session Expired")
    st.warning("Your session has expired. You will be redirected to the login page.")
    
    # Placeholder for a countdown before redirect
    with st.spinner("Redirecting in 3 seconds..."):
        time.sleep(3)
    
    st.switch_page("pages/auth.py") # Redirect to the login page

def render_loading_page():
    """
    Renders a loading state page (P42).
    """
    st.set_page_config(page_title="Loading...", layout="centered")
    with st.spinner("Loading, please wait..."):
        st.write("### 💡 Tip: The more detailed your symptom description, the better the AI can assist you.")
        time.sleep(5) # Simulate a loading process
    st.success("Loaded!")

# Example of how to call these functions
if __name__ == "__main__":
    PAGES = {
        "404 Not Found": render_404_page,
        "500 Server Error": render_500_page,
        "Access Denied": render_access_denied_page,
        "Maintenance": render_maintenance_page,
        "Session Expired": render_session_expired_page,
        "Loading": render_loading_page,
    }
    
    st.sidebar.title("Error Page Examples")
    selection = st.sidebar.radio("Go to", list(PAGES.keys()))
    page = PAGES[selection]
    page()
