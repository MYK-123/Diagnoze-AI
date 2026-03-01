import streamlit as st
from utils.api_connect import get_api_client

_GENDER_MAP = {
    "Prefer not to say": "prefer_not_to_say",
    "Male": "male",
    "Female": "female",
    "Other": "other",
}

_GENDER_LABELS = ["Prefer not to say", "Male", "Female", "Other"]
_GENDER_LABEL_FROM_VALUE = {v: k for k, v in _GENDER_MAP.items()}

def render_profile_page(router):
    """User profile page"""
    st.title("👤 Profile Settings")
    
    if st.button("Home"):
        router.redirect(*router.build("dashboard"))
    
    # Get user profile from API
    api = get_api_client()
    response = api.get_user_profile()
    
    if not response.get("success"):
        st.error("Unable to load profile")
        return
    
    profile = response["data"]
    
    # Tabs for different settings
    tab1, tab2, tab3, tab4 = st.tabs(["Personal Info", "Preferences", "Privacy", "Account"])
    
    with tab1:
        st.subheader("Personal Information")
        
        with st.form("personal_info_form"):
            col1, col2 = st.columns(2)
            with col1:
                first_name = st.text_input("First Name", value=profile.get("first_name", ""))
                email = st.text_input("Email", value=profile.get("email", ""))
            with col2:
                last_name = st.text_input("Last Name", value=profile.get("last_name", ""))
                phone = st.text_input("Phone", value=profile.get("phone", ""))
            
            age = st.number_input("Age", min_value=1, max_value=120, 
                                  value=profile.get("age", 25))
            current_gender_value = profile.get("gender", "prefer_not_to_say")
            current_gender_label = _GENDER_LABEL_FROM_VALUE.get(current_gender_value, "Prefer not to say")
            gender_label = st.selectbox(
                "Gender",
                _GENDER_LABELS,
                index=_GENDER_LABELS.index(current_gender_label),
            )
            
            if st.form_submit_button("Save Changes", type="primary"):
                update_data = {
                    "first_name": first_name,
                    "last_name": last_name,
                    "email": email,
                    "phone": phone,
                    "age": int(age),
                    "gender": _GENDER_MAP.get(gender_label, "prefer_not_to_say"),
                }
                
                update_response = api.update_user_profile(update_data)
                if update_response.get("success"):
                    st.success("Profile updated successfully!")
                else:
                    st.error("Failed to update profile")
    
    with tab2:
        st.subheader("Preferences")
        
        st.write("**Notification Settings**")
        email_notifications = st.checkbox("Email notifications", 
                                          value=profile.get("preferences", {}).get("email_notifications", True))
        health_tips = st.checkbox("Health tips and reminders",
                                  value=profile.get("preferences", {}).get("health_tips", True))
        
        st.write("**Chat Preferences**")
        default_symptom_mode = st.radio(
            "Default symptom input mode:",
            ["Text input", "Quick select", "Voice input"],
            index=["Text input", "Quick select", "Voice input"]
            .index(profile.get("preferences", {}).get("symptom_mode", "Text input"))
        )
        
        if st.button("Save Preferences", key="save_prefs"):
            st.info("Preferences saved (mock)")
    
    with tab3:
        st.subheader("Privacy Settings")
        
        st.write("**Data Sharing**")
        share_anonymous = st.checkbox(
            "Share anonymous data to improve AI (recommended)",
            value=profile.get("privacy", {}).get("share_anonymous", True)
        )
        
        save_chat_history = st.checkbox(
            "Save my chat history",
            value=profile.get("privacy", {}).get("save_history", True)
        )
        
        st.write("**Data Management**")
        if st.button("Export All My Data"):
            st.info("Data export feature coming soon")
        
        if st.button("Delete Chat History"):
            if st.checkbox("I understand this action cannot be undone"):
                if st.button("Confirm Delete", type="secondary"):
                    st.warning("History deleted (mock)")
    
    with tab4:
        st.subheader("Account Settings")
        
        st.write("**Change Password**")
        with st.form("password_form"):
            current_password = st.text_input("Current Password", type="password")
            new_password = st.text_input("New Password", type="password")
            confirm_password = st.text_input("Confirm New Password", type="password")
            
            if st.form_submit_button("Change Password"):
                if new_password != confirm_password:
                    st.error("New passwords do not match")
                elif len(new_password) < 8:
                    st.error("Password must be at least 8 characters")
                else:
                    st.success("Password changed (mock)")
        
        st.write("**Account Status**")
        st.info(f"Account created: {profile.get('created_at', 'Unknown')}")
        st.info(f"Last login: {profile.get('last_login', 'Unknown')}")
        
        st.write("**Danger Zone**")
        if st.button("Delete My Account", type="secondary"):
            st.error("Account deletion feature coming soon")

if __name__ == "__main__":
    render_profile_page(None)


